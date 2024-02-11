use noise::{Fbm, NoiseFn, Perlin};
use whiskers::prelude::*;

#[sketch_app]
struct Ptpx2024Sketch {
    #[param(slider, min = 2, max = 80)]
    columns: usize,
    #[param(slider, min = 2, max = 80)]
    rows: usize,
    #[param(slider, min = 0.0, max = 5.0)]
    spacing: Length,
    #[param(slider, logarithmic, min = 0.1, max = 2.0)]
    cell_size: Length,

    #[param(slider, logarithmic, min = 0.0001, max = 1.0)]
    noise_frequency: f64,

    #[param(slider, min = -1.0, max = 1.0)]
    noise_offset: f64,

    #[param(slider, logarithmic, min = 0.1, max = 5.0)]
    noise_gain: f64,

    #[param(slider, min = -1.0, max = 1.0)]
    ramp_offset: f64,

    #[param(slider, logarithmic, min = 0.1, max = 20.0)]
    ramp_gain: f64,

    #[param(slider, min = 0.1, max = 5.0)]
    dash_size: Length,

    #[param(slider, min = 0., max = 1.)]
    dash_randomness: f64,
}

impl Default for Ptpx2024Sketch {
    fn default() -> Self {
        Self {
            columns: 16,
            rows: 13,
            spacing: 0.65 * Unit::Mm,
            cell_size: 0.42 * Unit::Cm,
            noise_frequency: 0.0055,
            noise_offset: 0.42,
            noise_gain: 0.8,
            ramp_offset: 0.19,
            ramp_gain: 3.2,
            dash_size: 0.57 * Unit::Mm,
            dash_randomness: 0.8,
        }
    }
}

impl App for Ptpx2024Sketch {
    fn update(&mut self, sketch: &mut Sketch, ctx: &mut Context) -> anyhow::Result<()> {
        sketch.stroke_width(0.2 * Unit::Mm);

        let grid = HexGrid::with_pointy_orientation();

        let fbm = &Fbm::<Perlin>::default();

        let noise_offset_x = ctx.rng_range(0.0..10000.0);
        let noise_offset_y = ctx.rng_range(0.0..10000.0);

        grid.cell_size(self.cell_size.into())
            .columns(self.columns)
            .rows(self.rows)
            .spacing(self.spacing.into())
            .build(sketch, |sketch, cell| {
                // choose color based on columns
                if self.columns > 1 {
                    let color_val = ((cell.column as f64
                        / (self.columns.saturating_sub(1) as f64))
                        + ctx.rng_range(-0.2..0.2))
                    .clamp(0.0, 1.0);

                    if color_val < 0.3333 {
                        sketch.color(Color::DARK_RED);
                        sketch.set_layer(1);
                    } else if color_val < 0.6666 {
                        sketch.color(Color::RED);
                        sketch.set_layer(2);
                    } else {
                        sketch.color(Color::GOLD);
                        sketch.set_layer(3);
                    }
                }

                // radial ramp
                let mut ramp = 2.0
                    * ((cell.center.x() / sketch.width()) - 0.5)
                        .hypot((cell.center.y() / sketch.height()) - 0.5)
                    + self.ramp_offset;

                ramp = (ramp - 0.5) * self.ramp_gain + 0.5;
                ramp = ramp.clamp(0.0, 1.0);

                let mut noise = 1.0
                    - (self.noise_gain
                        * fbm.get([
                            (cell.center.x() + noise_offset_x) * self.noise_frequency,
                            (cell.center.y() + noise_offset_y) * self.noise_frequency,
                        ])
                        + self.noise_offset)
                        * ramp;

                noise = noise.clamp(0.0, 1.0);

                // don't dash cells with low noise
                if noise < 0.75 {
                    let dash_px = self.dash_size.to_px::<f64>() * ctx.rng_range(0.8..1.2);
                    let dash_on = noise * dash_px;
                    let dash_off = 2.0 * (1. - noise) * dash_px;
                    let dash_randomness_range =
                        (1.0 - self.dash_randomness)..(1.0 + self.dash_randomness);
                    let dashes = [
                        dash_on * ctx.rng_range(dash_randomness_range.clone()),
                        dash_off * ctx.rng_range(dash_randomness_range.clone()),
                        dash_on * ctx.rng_range(dash_randomness_range.clone()),
                        dash_off * ctx.rng_range(dash_randomness_range.clone()),
                        dash_on * ctx.rng_range(dash_randomness_range.clone()),
                        dash_off * ctx.rng_range(dash_randomness_range),
                    ];

                    let cell: kurbo::BezPath = kurbo::dash(
                        cell.into_bezpath().into_iter(),
                        ctx.rng_range(0.0..5.0),
                        &dashes,
                    )
                    .collect();
                    sketch.add_path(cell);
                } else {
                    sketch.add_path(cell);
                }
            });

        Ok(())
    }
}

fn main() -> Result {
    Ptpx2024Sketch::runner()
        .with_page_size_options(PageSize::A6H)
        .with_layout_options(LayoutOptions::Center)
        .run()
}
