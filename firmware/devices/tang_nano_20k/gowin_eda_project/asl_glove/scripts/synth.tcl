# scripts/synth.tcl
# Synthesis only — use when iterating on HDL before committing to full flow

open_project asl_glove.gprj

run syn

close_project
puts "=== Synthesis complete ==="