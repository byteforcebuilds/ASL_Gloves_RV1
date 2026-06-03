# scripts/full_flow.tcl
# Runs synthesis, place & route, and bitstream generation in one shot

open_project asl_glove.gprj

run all

# Copy bitstream to bitstream/ folder so it gets committed
file mkdir bitstream
file copy -force \
    impl/pnr/asl_glove.fs \
    bitstream/asl_glove.fs

close_project
puts "=== Full flow complete. Bitstream saved to bitstream/asl_glove.fs ==="