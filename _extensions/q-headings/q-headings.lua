--[[
q-headings.lua

For every BlockQuote that begins with text like
    "Solution (Q1 — Identification of A–F)."
inject an h2 Header containing the part inside the parentheses, placed
immediately before the most recently seen OrderedList (which is presumed to
be the question the solution answers).

This means the user writes problems in the natural format

    1. **Identify** substances A–F.

    > **Solution (Q1 — Identification of A–F).**
    > ...

and the filter synthesizes

    ## Q1 — Identification of A–F

above the question, so Quarto's TOC sidebar shows one entry per sub-question.

If the qmd already contains an explicit Header right before the OrderedList,
the synthesized heading is suppressed (no duplicates).
--]]

-- Returns (inlines, plain_text) extracted from a Solution-style blockquote,
-- or (nil, nil) if the blockquote doesn't look like a solution block.
--
-- We walk the AST directly rather than stringify-then-reparse, because
-- pandoc.utils.stringify discards the $ delimiters around math content,
-- and re-parsing the resulting plain text as markdown rebuilds it as plain
-- text (not Math). Walking the AST lets us preserve Math, Emph, etc.
-- inlines verbatim inside the heading.
local function solution_inlines(blockquote)
  local first_para = blockquote.content and blockquote.content[1]
  if not first_para or not first_para.content then return nil, nil end

  -- The "**Solution (...)**" bold wraps the label; descend into the Strong
  -- if present so we work with the inner inlines.
  local container = first_para.content
  if #container >= 1 and container[1].t == "Strong" then
    container = container[1].content
  end

  -- Locate the "Solution" Str and the parentheses that follow it.
  local start_idx, start_off, end_idx, end_off
  local seen_solution = false
  for i, inline in ipairs(container) do
    if inline.t == "Str" then
      local s = inline.text
      if not seen_solution and s:find("Solution", 1, true) then
        seen_solution = true
      end
      if seen_solution then
        if not start_idx then
          local p = s:find("%(", 1)
          if p then start_idx = i; start_off = p end
        end
        if start_idx and not end_idx then
          local from = (i == start_idx) and (start_off + 1) or 1
          local p = s:find("%)", from)
          if p then end_idx = i; end_off = p end
        end
      end
    end
  end
  if not start_idx or not end_idx then return nil, nil end

  -- Extract inlines between the "(" and ")" boundaries.
  local label = {}
  for i = start_idx, end_idx do
    local inline = container[i]
    if inline.t == "Str" then
      local s = inline.text
      local seg
      if i == start_idx and i == end_idx then
        seg = s:sub(start_off + 1, end_off - 1)
      elseif i == start_idx then
        seg = s:sub(start_off + 1)
      elseif i == end_idx then
        seg = s:sub(1, end_off - 1)
      else
        seg = s
      end
      if seg ~= "" then table.insert(label, pandoc.Str(seg)) end
    else
      table.insert(label, inline)
    end
  end

  -- Trim leading/trailing Space inlines.
  while #label > 0 and label[1].t == "Space" do table.remove(label, 1) end
  while #label > 0 and label[#label].t == "Space" do table.remove(label) end
  if #label == 0 then return nil, nil end

  local plain = pandoc.utils.stringify(pandoc.Plain(label))
  return label, plain
end

-- Generate an anchor-safe slug from a label like "Q1 — Identification of A–F".
-- Quarto's auto-id pass has already run by the time this filter executes, so
-- we have to set the id explicitly or anchor links will be empty.
local function slugify(s)
  s = s:lower()
  -- Normalize common Unicode separators to ASCII hyphen (UTF-8 byte sequences).
  s = s:gsub("\xe2\x80\x94", "-")  -- em-dash U+2014
  s = s:gsub("\xe2\x80\x93", "-")  -- en-dash U+2013
  s = s:gsub("\xe2\x80\xa6", "-")  -- ellipsis U+2026
  -- Drop any remaining high-bit (non-ASCII) bytes.
  s = s:gsub("[\128-\255]", "")
  -- Collapse runs of whitespace/punctuation/control to a single hyphen.
  s = s:gsub("[^a-z0-9]+", "-")
  -- Strip leading/trailing hyphens.
  s = s:gsub("^%-+", ""):gsub("%-+$", "")
  if s == "" then s = "section" end
  return s
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then return nil end

  local blocks = doc.blocks
  local out = {}
  local last_list_pos = nil  -- 1-indexed position in `out` of most recent OrderedList
  local id_counter = {}      -- de-duplicate ids if the same label appears twice

  for _, block in ipairs(blocks) do
    if block.t == "OrderedList" then
      -- If the immediately preceding block is already a Header, the user has
      -- hand-authored a Q-heading and we should not shadow it.
      local prev = out[#out]
      if prev and prev.t == "Header" then
        last_list_pos = nil
      else
        last_list_pos = #out + 1
      end
      table.insert(out, block)
    elseif block.t == "BlockQuote" then
      local inlines, label = solution_inlines(block)
      if inlines and last_list_pos then
        local slug = slugify(label)
        id_counter[slug] = (id_counter[slug] or 0) + 1
        if id_counter[slug] > 1 then
          slug = slug .. "-" .. id_counter[slug]
        end
        local attr = pandoc.Attr(slug, { "anchored" }, {})
        local header = pandoc.Header(2, inlines, attr)
        table.insert(out, last_list_pos, header)
        last_list_pos = nil
      end
      table.insert(out, block)
    else
      table.insert(out, block)
    end
  end

  doc.blocks = out
  return doc
end
