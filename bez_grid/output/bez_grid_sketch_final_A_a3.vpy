eval "dx = 148.5*mm"
eval "dy = 105 * mm"

read bez_grid_sketch_final_A_0.svg
translate 0 %dy%

read bez_grid_sketch_final_A_1.svg
translate 0 %dy%

read bez_grid_sketch_final_A_2.svg
translate 0 %dy%

read bez_grid_sketch_final_A_3.svg

translate %dx% "%-dy * 3%"

read bez_grid_sketch_final_A_4.svg
translate 0 %dy%

read bez_grid_sketch_final_A_5.svg
translate 0 %dy%

read bez_grid_sketch_final_A_6.svg
translate 0 %dy%

read bez_grid_sketch_final_A_7.svg

pagesize a3
pagerotate

linesort

write bez_grid_sketch_final_A_a3.svg
