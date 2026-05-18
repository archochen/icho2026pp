--[[
status-badge.lua

Reads the `status:` field from a document's YAML frontmatter and:
  1. Inserts a colored badge span next to the title block in the rendered HTML.
  2. Exposes `status-class` and `status-label` metadata for use elsewhere.

Status values: not-started | draft | revised | final | tbc
Anything else is rendered with a generic gray badge.
--]]

local STATUS_LABELS = {
  ["not-started"] = "Not started",
  ["draft"]       = "Draft",
  ["revised"]     = "Revised",
  ["final"]       = "Final",
  ["tbc"]         = "TBC",
}

local function normalize(s)
  return (s or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
end

local current_status_class = nil
local current_status_label = nil

function Meta(meta)
  local raw = pandoc.utils.stringify(meta.status or "")
  raw = normalize(raw)
  if raw == "" then return nil end

  local label = STATUS_LABELS[raw] or (raw:sub(1,1):upper() .. raw:sub(2))
  current_status_class = "status-" .. raw
  current_status_label = label

  -- expose to templates / listings
  meta["status-class"] = pandoc.MetaString(current_status_class)
  meta["status-label"] = pandoc.MetaString(label)
  return meta
end

-- Inject the badge immediately after the first Header (the title body) for HTML output.
function Pandoc(doc)
  if not current_status_class then return nil end
  if not quarto.doc.is_format("html") then return nil end

  local badge = pandoc.RawBlock(
    "html",
    string.format(
      '<p class="status-badge-line"><span class="status-badge %s">%s</span></p>',
      current_status_class,
      current_status_label
    )
  )

  -- Find first header (likely the implicit title); insert badge after it.
  -- Quarto's title-block is added later, so we just put it at the very top of body.
  table.insert(doc.blocks, 1, badge)
  return doc
end
