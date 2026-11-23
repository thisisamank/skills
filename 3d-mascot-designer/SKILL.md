---
name: 3d-mascot-designer
description: Design and build an animated 3D mascot for a product - discovery, character brief, 2D SVG concepts, turnaround and expression sheets, a Three.js build from primitives, an animation library with a state machine, and one shareable interactive preview page. On request it also gives GLB export, a Blender rebuild script and React / Three.js / Unity integration. Use whenever the user asks for a mascot, brand character, product character, animated helper or guide, a 3D character for a website, app, video or stickers, or wants to animate, rig, export or integrate a mascot they already have - also when they do not say "3D".
---

# 3D mascot designer

Take a product from "we want a mascot" to a live 3D character on a page the user can share. The work goes from cheap to expensive: words, then flat drawings, then 3D, then motion. Each step locks a decision before the next step makes it costly to change.

## Rules

- Do the steps in order. Do not start the 3D build before the user picks a concept. A change to an SVG takes a minute. A change to a rigged, animated model does not.
- Stop for the user two times: after the questions in step 1, and after the concepts in step 3. After the user picks a concept, do steps 4 to 7 in one run, unless the user asked to approve each step.
- Start the 3D work from `assets/preview-template.html`. Do not write the page from zero. The template has a tested state machine, a self-test, mobile layout and the export code. Your work is the shape, the colors and the motion.
- Make an original character. Mascots the user likes tell you the direction ("round, calm, big eyes"). Do not copy their shapes, faces or names.
- Say what the method cannot do. See "Limits" at the end.

## Files in this skill

| File | Use |
|---|---|
| `references/design.md` | Steps 1 to 4: questions, brief template, SVG rules, turnaround and expression recipes. Read it before step 1. |
| `references/build.md` | Steps 5 to 7: template map, how to change the shape, pose channels, how to write clips, timing, tests. Read it before step 5. |
| `references/handoff.md` | Step 8: GLB, Blender, React / Three.js / Unity. Read it only when the user asks for handoff. |
| `assets/sheet-template.html` | Page for SVG concepts, turnaround and expressions. It adds a small black silhouette row to each drawing. |
| `assets/preview-template.html` | The working 3D mascot page: rig, materials, light, shadow, 7 clips, state machine, panel, tests, exports. |
| `scripts/mascot_tools.py` | `inline` (one self-contained file), `qa` (contact sheet and self-test), `shot` (screenshots), `module`, `rig`, `glb`, `cleanup` (kill all headless browsers it started). |
| `scripts/rebuild_in_blender.py` | Rebuilds the mascot in Blender with bones, shape keys and keyframed actions. |

## Step 1. Discovery

First read what the project already tells you: landing page, README, theme or Tailwind config, logo files. Then ask only for what is missing, in one message:

1. The product and its audience.
2. Three personality adjectives.
3. Brand colors (hex values if they have them).
4. Where the mascot will live: website, app, videos, stickers.
5. Mascots they like or dislike, and why.

State what you found yourself ("I took the colors from `tailwind.config.ts`: ...") so the user can correct it. If the user says "you decide", choose, and write the choices as assumptions in the brief.

## Step 2. Character brief

Write the brief in the chat. Keep it to one screen. Use the template in `references/design.md`: name ideas, personality, role (guide, helper or cheerleader - pick one), how it moves, what it never does, and the limits that come from where it lives (smallest size, formats).

The "how it moves" line matters later. It selects the timing preset in step 6 (calm, friendly or energetic).

## Step 3. 2D concepts

Draw 3 or 4 concepts as SVG in a copy of `assets/sheet-template.html`. The concepts must differ in base shape and in the one feature that marks the silhouette (ears, antenna, tail, hat). Four colors of one shape are one concept.

Rules for each drawing, with the reasons:

- Simple base shapes: circles, ellipses, rounded rectangles. Each one must map to a sphere, a capsule or a lathe shape, or step 5 cannot build it.
- A strong silhouette. The black row under each card is the test. If two concepts look the same in black, change one.
- Big head, big eyes. The face carries the emotion, and it must read at 32 px.
- 2 to 4 brand colors, through the CSS variables at the top of the sheet. No gradients, no thin lines, no fine detail. Detail disappears at small size and cannot be built from primitives.

Show the concepts side by side: open the page for the user, or publish it. Give each concept a name, one line on the idea, and say which one you recommend and why. Then ask which one to develop, and stop.

## Step 4. Turnaround and expressions

For the chosen concept, add two sections to the sheet:

- Turnaround: front, side, back and three-quarter views with the same guide lines in each view (top of head, eye line, neck, ground). The side view fixes the depth of every part. The 3D build takes its sizes from these views.
- Expressions: happy, sad, surprised, thinking, confused, excited. Use only what the 3D face can do: eye open or closed, eye size, look direction, mouth curve, mouth open, head tilt, body pose. Write the channel values under each drawing. They become the poses of the clips in step 6. The recipes are in `references/design.md`.

## Step 5. 3D build

Read `references/build.md`. Copy `assets/preview-template.html` to the working directory, for example `<name>-mascot.html`. Then change it:

- Set the name, tagline, colors, material and personality in `MASCOT_DEFAULTS`.
- Rebuild the "Build" section from primitives (spheres, capsules, lathe shapes, tubes) to match the turnaround.
- Keep the hierarchy: `root > hips > (body, feet, arms, head > (face > eyes, mouth; extras))`. Each part that moves alone is a bone with its pivot at the joint. Without this, parts cannot animate independently, and the exports fail.
- Choose the material from the personality. Glossy toy: playful, energetic, tech. Soft clay: warm, calm, handmade. Toon: bold, graphic, flat brand style.
- Keep the soft light and the ground shadow from the template.

## Step 6. Animation library

The template has all the required clips: idle (breathing, blinking, sway), wave, celebrate, thinking / loading, sad / error, point, talk, and eyes that follow the pointer. Adapt them to the new shape and the personality. Do not only rename them.

- Each clip must show the principles: squash and stretch, anticipation before a big move, follow-through and overlap (head after body, springs on loose parts), and easing on every key. `references/build.md` shows how each one looks in the code.
- Match the timing to the personality with the `PERSONALITIES` preset, then tune single clips. A calm mascot does not spin in the air.
- Keep the state machine. `play(name)` cross-fades from the pose on screen. One-shot clips return to idle. Loop clips run until `stop()`.
- Loop clips must repeat exactly. One-shot clips must start and end at the rest pose. The self-test checks both.

## Step 7. Preview page

1. Run the checks (see "Quality checks").
2. Make the page self-contained: `python3 scripts/mascot_tools.py inline <name>-mascot.html <name>-preview.html`. The result has three.js inside, so it works offline and on hosts that block other domains.
3. Publish the inlined page so the user can share it: use the Artifact tool when the session has one. If there is no publish tool, give the file and say that any static host can serve it as one file.
4. Tell the user what the page has: a button for each animation, personality and material switches, color controls, and "Copy settings", which gives the chosen colors back as text. An address like `?material=clay&body=ff7a59` shares one variant.

Keep `<name>-mascot.html` (the build before `inline`). Later edits and the GLB export use it.

## Step 8. Handoff (only on request)

Read `references/handoff.md`. It gives the three deliverables:

- GLB with every clip baked: `mascot_tools.py glb`, or the "Download GLB" button on `<name>-mascot.html?handoff`.
- Blender: `mascot_tools.py rig` writes the rig data, and `rebuild_in_blender.py` rebuilds the model with bones, shape keys and keyframed actions.
- Integration snippets for React, plain Three.js and Unity that start animations from app events.

## Quality checks

Do these before you deliver. Fix what fails, then run them again.

| Check | How |
|---|---|
| The silhouette reads at small size | `mascot_tools.py qa page.html sheet.png`, then look at the bottom row of the image (128, 64, 32, 16 px). |
| Animations loop cleanly | The self-test in the `qa` output. It reports a jump or a hitch at the loop seam, and one-shot clips that do not start or end at rest. |
| No parts clip through each other | The self-test measures the pairs in `NO_CLIP`. Also look at every frame of the contact sheet. The test only knows the pairs you list. |
| The page works on mobile | `mascot_tools.py shot page.html phone.png --mobile`, then look at it: the mascot is fully in view, no button is cut, the panel scrolls. |

### Headless browsers: always kill them

`qa`, `shot`, `rig` and `glb` start a headless browser that draws WebGL on the CPU. One browser that stays open uses one to two full CPU cores until something kills it. Many left-over browsers can fill all CPUs, all RAM and swap. This happened: 46 browsers were left open for 10 hours.

- Run these commands in the foreground, one at a time. Give the shell command a timeout of at least 200 s (200000 ms). `qa` can wait 150 s, and a tool timeout kills the script before it can close its browser.
- Do not run them in the background, and do not start a second run while the first one is still running.
- After the last headless command, and always before you deliver or stop (also after a failure, a timeout or an interrupt), run `python3 scripts/mascot_tools.py cleanup`.
- Then make sure that no browser stays open: `pgrep -fc 'mascot-browser-'` must print `0`. If it does not, run `pkill -9 -f 'user-data-dir=.*mascot-browser-'` and do the check again.
- Never kill the user's own browser. Kill only processes that use a `mascot-browser-*` profile.

The script also kills its browser (the whole process group) when it ends, fails or gets SIGTERM, and each new run kills browsers that earlier runs left. These protections do not work when the script gets SIGKILL and no new run follows. Thus the `cleanup` step is always necessary.

The `qa` and `shot` commands need a Chrome-family browser. If there is none, open the page with `?qa` yourself if you can. If you cannot run a browser at all, check the clip code by hand (loop periods divide the duration, one-shots start and end at rest), tell the user which checks you could not run, and ask them to open the page on a phone.

## Limits

Say this to the user at the right moment, in plain words. Do not hide it and do not over-promise.

- A mascot built in code suits simple, rounded, toy-like styles: shapes that are spheres, capsules and lathe forms.
- It does not suit detailed or realistic characters: fur, cloth, fingers, a sculpted face, a likeness of a real person or animal. For these, recommend a 3D artist or an image-to-3D tool for the model.
- In that case, offer the part this skill still does well: rigging, the animation logic and state machine, and the integration into the app.
- A code-built face has a small set of expressions (the pose channels). If the brief needs subtle acting, say so early.
