def tree [path: string, depth: int, prefix: string] {
  let entries = ls $path | sort-by type name
  let last_index = ($entries | length) - 1
  $entries | enumerate | each {|entry|
    let file = $entry.item
    let is_last = $entry.index == $last_index
    let branch = if $is_last { "└── " } else { "├── " }
    let row = {
      name: $"($prefix)($branch)($file.name | path basename)"
      type: $file.type
      size: $file.size
      modified: $file.modified
    }
    if $file.type == dir and $depth > 1 {
      let child_prefix = if $is_last { $"($prefix)    " } else { $"($prefix)│   " }
      [$row] | append (tree $file.name ($depth - 1) $child_prefix)
    } else {
      [$row]
    }
  } | flatten
}

def main [path: string = ".", depth: int = 2] {
  tree $path $depth ""
}
