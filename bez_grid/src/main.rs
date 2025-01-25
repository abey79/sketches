use noise::{Fbm, NoiseFn, Perlin};
use whiskers::prelude::*;

fn main() -> Result {
    BezGridSketch::runner()
        .with_page_size_options(PageSize::Custom(148.5, 105.0, Unit::Mm))
        .with_layout_options(LayoutOptions::default())
        .run()
}

// --

#[sketch_app]
struct BezGridSketch {
    #[param(min = 1.0, step = 1.0)]
    base_cell_size: f64,

    #[param(logarithmic, min = 0.01, max = 10.0)]
    offset: Length,

    #[param(min = 1, step = 1)]
    column: usize,

    #[param(min = 1, step = 1)]
    rows: usize,

    #[param(logarithmic, min = 0.001, max = 1.0)]
    noise_speed: f64,
}

impl Default for BezGridSketch {
    fn default() -> Self {
        Self {
            base_cell_size: 20.5,
            offset: 0.45 * Unit::Mm,
            column: 25,
            rows: 16,

            noise_speed: 0.01,
        }
    }
}

impl App for BezGridSketch {
    fn update(&mut self, sketch: &mut Sketch, ctx: &mut Context) -> anyhow::Result<()> {
        let grid_width = self.column as f64 * self.base_cell_size;
        let grid_height = self.rows as f64 * self.base_cell_size;

        sketch.translate(
            (sketch.width() - grid_width) / 2.0,
            (sketch.height() - grid_height) / 2.0,
        );

        self.draw_grid(
            sketch,
            ctx,
            0.0,
            2,
            0,
            ColorMode::Gradient(2, Color::RED, 3, Color::DARK_RED),
        );

        sketch.push_matrix_and(|sketch| {
            let gutter = self.base_cell_size / 4.0;
            sketch.translate(gutter, gutter);

            self.draw_grid(
                sketch,
                ctx,
                gutter,
                2,
                1,
                ColorMode::Fixed(1, Color::gray(200)),
            );
        });

        Ok(())
    }
}

enum ColorMode {
    Fixed(usize, Color),
    Gradient(usize, Color, usize, Color),
}

impl BezGridSketch {
    fn draw_grid(
        &self,
        sketch: &mut Sketch,
        ctx: &mut Context,
        gutter: f64,
        stride: usize,
        stride_offset: usize,
        col_mode: ColorMode,
    ) {
        let cell_size = self.base_cell_size - gutter;
        let half_diag = cell_size / 2.0_f64.sqrt();
        let offset = self.offset.to_px::<f64>();
        let steps = (half_diag / offset).ceil() as i32;

        let fbm = Fbm::<Perlin>::default();
        let fbm_x_offset = ctx.rng_range(0.0..100.0);
        let fbm_y_offset = ctx.rng_range(0.0..100.0);

        Grid::from_cell_size([cell_size, cell_size])
            .columns(self.column)
            .rows(self.rows)
            .horizontal_spacing(gutter)
            .vertical_spacing(gutter)
            .build(sketch, |sketch, cell| {
                if (cell.column + cell.row) % stride != stride_offset {
                    return;
                }

                if matches!(col_mode, ColorMode::Gradient(..)) {
                    if ctx.rng_weighted_bool((cell.position.y() / sketch.height()).powf(2.0)) {
                        return;
                    }
                } else {
                    // if ctx.rng_weighted_bool(
                    //     ((sketch.height() - cell.position.y()) / sketch.height()).powf(4.0),
                    if ctx.rng_weighted_bool((cell.position.y() / sketch.height()).powf(2.0)) {
                        return;
                    }
                }

                let d = loop {
                    let dx = fbm.get([
                        cell.column as f64 * self.noise_speed,
                        cell.row as f64 * self.noise_speed + fbm_x_offset,
                    ]);
                    let dy = fbm.get([
                        cell.column as f64 * self.noise_speed + fbm_y_offset,
                        cell.row as f64 * self.noise_speed,
                    ]);

                    break kurbo::Vec2::new(dx, dy).normalize();

                    if dx != 0.0 || dy != 0.0 {
                        break kurbo::Vec2::new(dx, dy).normalize();
                    }
                };
                let n = kurbo::Vec2::new(-d.y, d.x).normalize();

                let center = kurbo::Point::new(
                    cell.position.x() + cell_size / 2.0,
                    cell.position.y() + cell_size / 2.0,
                );

                for cur_step in -steps..=steps {
                    let prob = cell.position.x() / sketch.width();

                    let p = center + n * (cur_step as f64 * offset);
                    let start = p + d * -half_diag;
                    let end = p + d * half_diag;

                    let line = kurbo::Line::new(start, end);

                    let mut path = vsvg::Path::from(line);
                    path.crop(
                        cell.position.x(),
                        cell.position.y(),
                        cell.position.x() + cell_size,
                        cell.position.y() + cell_size,
                    );

                    match col_mode {
                        ColorMode::Fixed(layer, color) => {
                            sketch.set_layer(layer);
                            sketch.color(color);
                        }
                        ColorMode::Gradient(l1, c1, l2, c2) => {
                            //TODO: add this clamp to the function!
                            if ctx.rng_weighted_bool(prob.clamp(0.0, 1.0)) {
                                sketch.set_layer(l1);
                                sketch.color(c1);
                            } else {
                                sketch.set_layer(l2);
                                sketch.color(c2);
                            }
                        }
                    }

                    sketch.add_path(path.data);
                }
            });
    }
}
