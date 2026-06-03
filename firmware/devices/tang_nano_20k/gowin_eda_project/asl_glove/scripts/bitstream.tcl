# scripts/bitstream.tcl
# Bitstream generation only — assumes PnR already complete

open_project asl_glove.gprj

run bs

# Copy to bitstream/ for committing
file mkdir bitstream
file copy -force \
    impl/pnr/asl_glove.fs \
    bitstream/asl_glove.fs

close_project
puts "=== Bitstream generation complete. Saved to bitstream/asl_glove.fs ==="