import { mkdir } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const mapDirectory = path.resolve("public/maps");
const maps = [
  { name: "logres-player-map-circa-510", widths: [640, 960, 1240] },
  { name: "salisbury-county-circa-510", widths: [640, 1200, 2000, 2400] },
];

await mkdir(mapDirectory, { recursive: true });

for (const map of maps) {
  const source = path.join(mapDirectory, `${map.name}.jpg`);
  for (const width of map.widths) {
    const resized = sharp(source).resize({ width, withoutEnlargement: true });
    await Promise.all([
      resized.clone().avif({ quality: 58, effort: 6 }).toFile(path.join(mapDirectory, `${map.name}-${width}.avif`)),
      resized.clone().webp({ quality: 78, effort: 6 }).toFile(path.join(mapDirectory, `${map.name}-${width}.webp`)),
    ]);
  }
}
