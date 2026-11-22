# Build: steps 5 to 7

## Contents
1. Map of the template
2. Space and scale
3. Build the shape
4. Common shape changes
5. Pose channels
6. Write a clip
7. The animation principles in this code
8. Timing and personality
9. State machine and API
10. Tests
11. Mobile and speed

## 1. Map of the template

`assets/preview-template.html` is one file. The script has five parts, each under a banner comment.

| Part | What it holds | Change it? |
|---|---|---|
| MASCOT (between `MASCOT:BEGIN` and `MASCOT:END`) | Config, materials, build, pose, clips, state machine, layers, tests. It needs only THREE and does not touch the page. | Yes. This is the mascot. |
| STAGE | Renderer, camera, studio reflections, lights, ground shadow, pointer input | Only the camera frame, if the mascot is much taller or wider |
| PANEL | Buttons, personality, material, colors, copy settings | Rarely. Buttons come from the clip list. |
| HANDOFF | `bakeClips`, `exportGLB`, `exportRig` | No |
| QA | Contact sheet and report for `?qa` | No |

Keep the `THREE:BEGIN` and `MASCOT:BEGIN` markers. The tools find the blocks by them. Do not use the three.js version in the import map as a reason to change it: `inline` needs version 0.170.0, the last one with a one-file module build.

## 2. Space and scale

- Y is up. The mascot faces +Z, toward the camera. The ground is y = 0.
- The mascot is about 2 units tall. The camera frames a box 3.0 wide and 3.4 high, which leaves room for a jump. If the mascot is larger, change `frameCamera`.
- "L" is the mascot's left. That is +X, the viewer's right.
- Angles are in radians. Time is in seconds.

## 3. Build the shape

Three helpers make every object:

- `bone(name, parent, x, y, z)`: a group that animations move. Put it at the joint: neck, shoulder, the base of an ear or tail.
- `group(name, parent, x, y, z)`: a group for placement only, for example the pivot that puts an eye on the head surface.
- `mesh(name, geometry, slot, parent, position, scale)`: a visible part. `slot` is the color: `body`, `accent`, `dark` or `light` (white, not lit).

Rules, with reasons:

- The hierarchy is `root > hips > (body, feet, arms, head > (face, extras))`. `hips` sits on the ground, so squash and stretch keep the feet on the floor.
- Give each object a unique name in camelCase with no spaces or dots. The GLB and Blender exports address objects by name.
- Put scale on meshes, not on bones. The one exception is `hips`, which the squash channel scales. A scaled bone with a turned rest pose cannot be rebuilt in Blender without shear.
- Use 2 to 4 colors, only through slots. Then recolor and material changes are one call.
- Stay under about 30 meshes, with spheres at 32 x 20 segments or less. Phones draw this easily.
- Face parts go on the head surface. `surface(yaw, pitch)` returns the distance from the head center to the surface in a direction. Use it as the z position of a part inside a pivot that has that yaw and pitch. If the head is not an ellipsoid, replace the function.

Primitives and when to use them:

| Primitive | Good for |
|---|---|
| `SphereGeometry` with a mesh scale | head, hands, feet, eyes, cheeks, belly patch |
| `CapsuleGeometry` | arms, legs, ears, antenna, tail parts |
| `LatheGeometry` from a profile | body shapes with a waist or a flat base: gumdrop, bell, drop, cup, hat |
| `TubeGeometry` along a curve | mouth line, whiskers, a thin tail |
| `TorusGeometry` | rings, a collar, glasses |

For a lathe body, list profile points from the bottom center to the top center as (radius, height), pass them through `SplineCurve` as the template does, and keep the first and last radius at 0 so the shape is closed.

## 4. Common shape changes

- Ears, tail, hair tuft: make a bone at the base and drive it the way the antenna is driven (see `stepSpring`). Copy the spring for each loose part and give long parts a lower stiffness. Do not keyframe them. The spring is the follow-through.
- No arms: remove the arm bones and the four arm channels. Wave with a whole-body tilt and a hop, or with an ear. Point with a lean and a look.
- No legs, it floats: remove the feet, raise `hips` to about 0.35, and add a slow rise and fall to `idlePose` through `p.y`. The shadow shows the height.
- Eyes with a white and a pupil: make the white a flat sphere on the surface and the pupil a smaller dark sphere in front. Make `lookX` and `lookY` move the pupil inside the white and leave the white still.
- Head and body in one piece: keep the `head` bone, put it at the center of the shape with no mesh of its own, and attach the face to it. Head channels then tilt only the face a little. Reduce their sizes in the clips.
- Brows: add two small capsules above the eyes and a `brow` channel that turns them. Add it to `FACE`.

After a shape change, update `NO_CLIP` with the pairs that can now collide, for example an ear and a raised hand.

## 5. Pose channels

Every clip writes to one pose object. `applyPose` turns the pose into transforms. This is why any two states can blend.

| Channel | Meaning | Typical range |
|---|---|---|
| `y` | height above the ground | 0 to 0.9 |
| `yaw` | turn of the whole mascot | a full turn in the jump |
| `squash` | negative is squashed, positive is stretched. Volume stays constant. | -0.25 to 0.25 |
| `lean`, `pitch` | body tilt to the side and to the front, from the feet | -0.1 to 0.1 |
| `headYaw`, `headPitch`, `headRoll` | head turn, nod (positive is down) and tilt (positive is toward the mascot's right) | -0.4 to 0.4 |
| `armLRaise`, `armRRaise` | arm out to the side and up, from the rest angle | -0.6 to 1.8 |
| `armLFwd`, `armRFwd` | arm to the front | 0 to 1.9 |
| `blink` | 0 open, 1 closed | 0 to 1 |
| `eyeWide` | bigger eyes | 0 to 1 |
| `lookX`, `lookY` | eye direction. Positive X is the viewer's right. Positive Y is up. | -1 to 1 |
| `mouthOpen` | 0 closed, 1 open | 0 to 1 |
| `smile` | 1 smile, 0 flat, -1 frown. Rest is 0.6. | -1 to 1 |

To add a channel: add it to `REST`, read it in `applyPose`, and write it in the clips. If it changes the face and not a bone, also add it to `FACE`, so the Blender export makes a shape key for it. If it has a left and right side, add it to `mirror`.

## 6. Write a clip

A clip is a function of time. It gets `t` in seconds and a pose `p` that starts at `REST`, and it sets channels.

```js
nod: { label: 'Nod', duration: 1.0, look: .5, pose(t, p) {
  p.squash    = track(t, [[0, 0], [.12, .03, 'out'], [.3, -.05, 'out'], [.6, 0]]);
  p.headPitch = track(t, [[0, 0], [.12, -.08, 'out'], [.3, .28, 'inOut'], [.52, -.04, 'out'], [.8, 0]]);
  p.smile     = track(t, [[0, .6], [.3, .9, 'out'], [1, .6]]);
} },
```

- `track(t, keys)` reads keyframes `[time, value, ease]`. The ease belongs to the move that ends at that key. Eases: `linear`, `in`, `out`, `inOut` (the default), `back` (goes past the value, then settles).
- `wave(t, period, phase)` is a sine. Use it for loops.
- Options on a clip: `loop`, `look` (how much the eyes follow the pointer, 0 to 1), `idleMix` (how much of the idle breathing stays on top, default 0.5), `label` (the button text).
- A new clip gets a button without more work. The panel reads the clip list.

Two rules that the self-test checks:

- A one-shot clip starts and ends at `REST`: each track begins and ends at the rest value of its channel (0, or 0.6 for `smile`).
- A loop clip repeats exactly: every `wave` period divides the duration (duration 3: periods 3, 1.5, 1, 0.75). Do not use `Math.abs` of a sine for a loop. It makes a corner at the seam. Square the sine.

`play('point', { mirror: true })` plays any clip to the other side.

## 7. The animation principles in this code

Each clip needs all four. A clip without them moves like a machine.

| Principle | How it looks in a clip | Example in the template |
|---|---|---|
| Squash and stretch | The `squash` channel. Squash on a crouch and a landing, stretch on a launch and a fall. | `celebrate`: `-.2` crouch, `.22` launch, `-.24` landing, `.07` rebound |
| Anticipation | A small move the opposite way, 0.12 to 0.22 s, before the main move | `wave`: the arm goes `-.12` and the body dips before the arm goes up. `point`: the reach starts at `-.16`. |
| Follow-through and overlap | Parts arrive at different times. The body leads, the head follows 0.05 to 0.1 s later. Loose parts use a spring. The `back` ease goes past the target. | `idlePose`: head phase `-.7` behind the lean. `point`: eyes at 0.26 s, head at 0.42 s. The antenna spring. |
| Easing | No `linear` on a body part. `out` for a move that lands, `in` for a fall, `inOut` for a slow change. | Every `track` key |

Also: the eyes move first, then the head, then the body. The pointer follow does this with two speeds (16 and 5 per second).

## 8. Timing and personality

`PERSONALITIES` sets four numbers for the whole mascot:

| Preset | tempo | bounce | sway | blend | Feels |
|---|---|---|---|---|---|
| calm | 0.8 | 0.65 | 0.7 | 0.40 s | slow, soft, heavy |
| friendly | 1.0 | 1.0 | 1.0 | 0.28 s | the default |
| energetic | 1.25 | 1.3 | 1.3 | 0.18 s | quick, light, springy |

`tempo` scales the clock. `bounce` scales `squash` and jump height. `sway` scales the idle. `blend` is the cross-fade time. Add a preset if the brief needs one, for example "elegant": tempo 0.9, bounce 0.5, sway 0.8, blend 0.45.

Then tune the clips for the character:
- Calm or serious: replace `back` with `out`, make holds longer, remove the spin (`spin: false` or delete the yaw track), make the jump lower.
- Energetic: shorter anticipation (0.1 s), larger overshoot, a second small hop after the landing.
- Fixed times that do not scale well: a blink is about 0.25 s, and a loading loop should be 2 to 4 s so it does not tire the user.

## 9. State machine and API

`createMascot(THREE, options)` returns the mascot object.

| Call | Effect |
|---|---|
| `mascot.root` | Add this to a scene |
| `mascot.update(dt)` | Call once per frame with seconds since the last frame |
| `mascot.play(name, { mirror, then, spin })` | Cross-fade to a clip. `then` names the clip that follows a one-shot. The default is idle. |
| `mascot.stop()` | Back to idle |
| `mascot.state` | Name of the current clip |
| `mascot.on('state', fn)`, `mascot.on('end', fn)` | A clip started, or a one-shot ended. Returns a function that removes the listener. |
| `mascot.lookAt(x, y)` | Where the eyes look, each from -1 to 1. (0, 0) is the viewer. |
| `mascot.setFollow(on)` | Turn the pointer follow on or off |
| `mascot.setColors({ body, accent, dark })`, `setMaterial(style)`, `setPersonality(name)` | Change the look and the timing while it runs |
| `mascot.setReducedMotion(on)` | Lower jump, no spin. The page sets it from the system setting. |

How the blend works: `play` stores the pose that is on screen and fades from it to the new clip over `blend` seconds. So a clip can interrupt any other clip at any time without a jump. A one-shot that starts from idle uses a short fade (0.12 s) so its anticipation is not washed out.

Three layers sit on top of every state: the blink (random, 2 to 6 s apart), the pointer follow, and the spring parts. Clips do not need to animate them.

## 10. Tests

```bash
python3 scripts/mascot_tools.py qa my-mascot.html sheet.png        # contact sheet + self-test report
python3 scripts/mascot_tools.py shot my-mascot.html phone.png --mobile --play wave --at 0.8
```

`qa` exits with code 1 when the self-test finds an issue. Then look at `sheet.png`: six frames of each clip, and the silhouette in black at 128, 64, 32 and 16 px from the front, turned and from the side. The pages load three.js from a CDN before `inline`, so `qa` on the first build needs a network. After `inline` it does not.

| Report line | Cause | Fix |
|---|---|---|
| `loop jumps` | A wave period does not divide the duration, or a track is used in a loop | Use periods that divide the duration |
| `loop has a hitch` | The value matches at the seam but the speed does not | Remove `Math.abs` or a track that ends on a slope |
| `does not start at REST` / `does not end at REST` | The first or last key is not the rest value | Start and end each track at the rest value |
| `parts clip` | Two parts in `NO_CLIP` overlap by more than 0.02 units | Lower the angle, bring the arm forward (`armFwd`), or tilt the head away |
| `goes below the ground` | `y` is negative | Keep `y` at 0 or above |
| `is not a number` | A track divides by zero: two keys with the same time | Give each key its own time |

The overlap test uses a sphere around each part. It is exact for sphere parts and too strict for long parts. So list hands, feet, ears and the head in `NO_CLIP`, not whole arms. The contact sheet is the second check for everything the test cannot see.

Read the silhouette row critically: at 32 px you must still see the head, the body and the signature feature. If the feature is gone, make it larger or thicker.

## 11. Mobile and speed

The template already does these. Keep them when you change the page.

- The canvas is sized by its box through a `ResizeObserver`, and the pixel ratio is capped at 2.
- On narrow screens the panel moves under the stage and the animation buttons scroll sideways. Buttons are 44 px high.
- `touch-action: pan-y` on the canvas: a vertical swipe scrolls the page and a horizontal drag turns the mascot.
- One shadow light with a 1024 map. No post-processing.
- If WebGL is not available, the page shows a short message instead of an empty box.
- The system "reduce motion" setting lowers the jump and removes the spin.
