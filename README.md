# sketches

My collection of personal plotter generative art sketches made with [vsketch](https://github.com/abey79/vsketch). Most can be run and interacted with using the following command:

```bash
$ vsk run hline
```

Some additional dependencies might be needed, including but not limited to:
- [vpype-explorations](https://github.com/abey79/vpype-explorations)
- [hatched](https://github.com/abey79/hatched)
- [vpype-text](https://github.com/abey79/vpype-text)

Though I wrote it, note that this code doesn't necessarily match my standards :)

The code is available under the MIT license and the artworks under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). 


---
### `machine_typography`

17 letters for 17 recipients. This is my winter '21-'22 [`#ptpx`](https://twitter.com/search?q=%23ptpx) contribution.

![IMG_1676_2200](https://user-images.githubusercontent.com/49431240/150769606-5d2f430c-4fa0-4326-a5ef-3090ca396d48.jpeg)

<img height="338" alt="image" src="https://user-images.githubusercontent.com/49431240/150769894-4add31e8-e975-466e-a9b9-7bcb8d66cb42.jpg"> <img height="338" alt="image" src="https://user-images.githubusercontent.com/49431240/150769907-eac67939-0e6a-4203-8769-e0031c06f210.jpg"> <img height="338" alt="image" src="https://user-images.githubusercontent.com/49431240/150769919-9faaba73-8bda-40d0-9151-1fd117f1b89a.jpg">


---

### `postcard`

Helper sketch to create postcards with addresses and a custom message. Very useful for `#ptpx`.

Instructions:

1) Create the following files next to the sketch script:
- `addresses.txt`: all the addresses, separated by two new lines
- `header.txt`: header text
- `message.txt`: postcard message, may contain $FirstName$, which will be replaced as you
  expect

2) Run: `vsk run postcard`

<img width="800" alt="image" src="https://user-images.githubusercontent.com/49431240/143276653-4fecfdd9-2131-4663-aed9-a9016bd54f00.png">


---
### `drift_poly`

My design for early 2021 `#ptpx`. The config for the 9 cards I made are included in the repo.

<img height="330" src="https://user-images.githubusercontent.com/49431240/112317144-0caf2300-8cac-11eb-887c-5178ad469a7d.jpeg" /><img height="330" src="https://user-images.githubusercontent.com/49431240/112317464-5e57ad80-8cac-11eb-90e4-efec9eebda51.png" /><img height="330" src="https://user-images.githubusercontent.com/49431240/112317151-0e78e680-8cac-11eb-94e9-c36af8359aa7.jpeg" />


---
### `dots`

Just a bunch of dots drawn with `vsk.point()` on a regular grid. Sometime they are skipped, sometime in a different color.

<img width="1000" src="https://user-images.githubusercontent.com/49431240/110030899-8c457400-7d36-11eb-9587-7aa57b8a0813.jpeg" />

---

### `random_lines`

That's 500k Perlin noise values obtained in a single call of [noise()](https://vsketch.readthedocs.io/en/latest/reference/vsketch.Vsketch.html#vsketch.Vsketch.noise).

<img width="300" src="https://user-images.githubusercontent.com/49431240/108544725-2c3ae080-72e7-11eb-8a4e-abd1922b823e.png" /><img width="300" src="https://user-images.githubusercontent.com/49431240/108545546-38736d80-72e8-11eb-8eb6-abfcbb8ebca6.jpeg" />


---

### `circular_patterns`

<img width="300" src="circular_patterns/output/circular_patterns_liked_1.svg" /><img width="300" src="https://pbs.twimg.com/media/EZwS1jAWoAABfA9?format=jpg&name=4096x4096" />

---

### `fish`

<img width="400" src="fish/output/fish_Hen_v4.svg" />

---

### `hline`

<img width="250" src="hline/output/hline_liked_1.svg" /><img width="250" src="hline/output/hline_liked_2.svg" /><img width="250" src="hline/output/hline_liked_3.svg" />

---

### `perlin agents`

<img width="600" src="perlin_agents/output/perlin_agents_liked_1.svg" />


