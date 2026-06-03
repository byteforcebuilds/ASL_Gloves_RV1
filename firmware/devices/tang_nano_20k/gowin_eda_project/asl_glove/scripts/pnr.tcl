# scripts/pnr.tcl
# Place and route only — assumes synthesis already complete

open_project asl_glove.gprj

run pnr

close_project
puts "=== Place and route complete ==="