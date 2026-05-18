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

local function solution_label(blockquote)
  local first = blockquote.content and blockquote.content[1]
  if not first then return nil end
  -- Use the AST inlines of the first paragraph; the leading "Solution" sits
  -- inside a Strong span in the user's format, so we have to look at the
  -- stringified text rather than the first inline alone.
  local text = pandoc.utils.stringify(first)
  -- Match: "Solution (Q1 — Identification of A–F)" — capture inside parens.
  -- Allow optional spaces and trailing punctuation after the closing paren.
  local label = text:match("^Solution%s*%(%s*(.-)%s*%)")
  return label
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
      local label = solution_label(block)
      if label and last_list_pos then
        local slug = slugify(label)
        id_counter[slug] = (id_counter[slug] or 0) + 1
        if id_counter[slug] > 1 then
          slug = slug .. "-" .. id_counter[slug]
        end
        local attr = pandoc.Attr(slug, { "anchored" }, {})
        local header = pandoc.Header(2, { pandoc.Str(label) }, attr)
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
