--[[
hide-cn-sections.lua

Removes the Chinese-language sections from HTML output by truncating the
document at the first Header whose stringified text matches one of the
configured marker phrases. Every block from there to end-of-document is
dropped — this matches the conventional structure of the user's problem
files, where Chinese content (中文版 / 相对丰度表 / 教学点评) always lives
in a contiguous tail block after the English content.

Source markdown is preserved verbatim. Only HTML output is affected.

A simple level-aware "skip until exit" algorithm doesn't work here because
the user's source mixes heading levels inside the Chinese block (the
section label is h2 `## 中文版 / Chinese translation` but the Chinese title
inside is h1 `# 第 23 题 ...`). Truncate-at-first-marker is robust to that.
--]]

local CN_MARKERS = {
  "中文版",
  "Chinese translation",
  "教学点评",
  "解题分析",
  "相对丰度表",
}

local function header_matches(header)
  local text = pandoc.utils.stringify(header)
  for _, pat in ipairs(CN_MARKERS) do
    if text:find(pat, 1, true) then return true end
  end
  return false
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then return nil end

  local out = {}
  local truncated = false

  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and header_matches(block) then
      truncated = true
      break
    end
    table.insert(out, block)
  end

  if truncated then
    -- Trim any trailing HorizontalRule(s) that were the separator leading
    -- into the now-dropped Chinese section.
    while #out > 0 and out[#out].t == "HorizontalRule" do
      table.remove(out)
    end
  end

  doc.blocks = out
  return doc
end
