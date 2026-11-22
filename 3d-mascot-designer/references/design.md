# Design: steps 1 to 4

## Contents
1. Discovery questions
2. Character brief template
3. SVG rules
4. Concepts
5. Turnaround
6. Expression sheet

## 1. Discovery questions

Ask in one message. Leave out each question that the conversation or the project files already answer.

1. What is the product, and who uses it?
2. Give three adjectives for the personality (for example: calm, clever, a little cheeky).
3. What are the brand colors? Hex values are best.
4. Where will the mascot live: website, app, videos, stickers? What is the smallest size?
5. Which mascots do you like or dislike, and why?

Why each answer matters:
- Audience and adjectives set the shape language (round = friendly, tall = elegant, pointed = sharp) and the timing.
- Colors: the mascot uses 2 to 4 of them. If the brand has one color, add a near-black for eyes and one accent, and say that you added them.
- Where it lives sets the limits. Stickers and favicons need a silhouette that reads at 32 px. Video allows more motion. An app needs short, quiet loops.
- Liked and disliked mascots tell you taste. Take the qualities, not the shapes.

## 2. Character brief template

Keep it to one screen.

```
# <Working name>: character brief

Name ideas   3 to 5 names, each with a short reason.
Personality  The three adjectives. For each: what it means for the shape and for the motion.
Role         Guide, helper or cheerleader. One. Then one sentence: what it does in the product.
How it moves Tempo (calm, friendly or energetic). Weight (light and bouncy, or soft and heavy).
             One signature move.
Never does   3 to 5 lines. Examples: never covers content, never laughs at an error,
             never loops a loud animation, never talks without a user action.
Lives in     Places and the smallest size. The formats that follow (page, GLB, stills).
Assumptions  What you decided because nobody said.
```

Roles in short. Guide: shows the way, uses point and talk. Helper: reacts to what the user does, uses thinking and sad. Cheerleader: rewards progress, uses celebrate and wave.

## 3. SVG rules

- Use `viewBox="0 0 200 240"`. The ground is at y = 220. Center the character at x = 100.
- Use only `circle`, `ellipse`, `rect` with `rx`, and simple `path` arcs.
- Fill with the sheet variables: `var(--body)`, `var(--accent)`, `var(--dark)`, `var(--light)`. Then one edit recolors every drawing.
- Group the parts the way the 3D model will be grouped: `limbs`, `body`, `head` with `eyes` inside. Give each group an id with a prefix for the card (`a-head`, `b-head`).
- No gradients, no filters, no strokes thinner than 3 units, no text inside the drawing.
- Head height is 45% to 60% of the full height. Eye width is at least 10% of the head width.
- Write `role="img"` and an `aria-label` on each `svg`.

Each shape must have a 3D primitive: circle or ellipse = sphere (scaled), rounded rectangle = capsule, a profile that turns around an axis = lathe, a thin curved line = tube. If you cannot name the primitive, simplify the shape.

## 4. Concepts

Make 3 or 4. Change the base shape and the silhouette feature between them. Useful axes:

| Axis | Options |
|---|---|
| Base shape | ball, bean or gumdrop, drop, rounded cube, bell |
| Head and body | one piece, head on a small body, head only with hands |
| Silhouette feature | ears, antenna, tail, hair tuft, hat, horn, leaf |
| Legs | feet only, short legs, none (it floats) |

Show them in one row in `assets/sheet-template.html`. The page adds a black row at 64, 32 and 16 px under each card. Look at that row before you show the page: each concept must be recognizable in black, and no two can look the same.

Under each card write the name and one line: the idea, and the adjective it serves. In the chat, recommend one and give the reason.

## 5. Turnaround

Four views of the chosen concept: front, side, back, three-quarter. Add the `guides` group from the template to each view, with the same y values in all four: top of head, eye line, neck, ground.

- Front: widths and the face.
- Side: depth. How far the face parts sit forward, how thick the body is, where a tail or backpack sits. Arms hang at the center line.
- Back: what is there when the face is not. If the back is empty, add one small feature (tail, tag, seam) so a turn in 3D is not blank.
- Three-quarter: check that the far eye and the far arm are still visible.

Then write a short size table from the drawing: for each part, the primitive and its size as a part of the full height. Step 5 scales these to a mascot about 2 units tall.

## 6. Expression sheet

Six head-and-shoulders drawings. Use only the things the 3D face can do. Under each, write the pose channels. Start from these recipes and adapt them to the character.

| Expression | Eyes | Mouth | Head and body | Channels |
|---|---|---|---|---|
| Happy | open, soft | wide smile | small tilt | `smile 1, headRoll 0.08` |
| Sad | half closed, look down | curve down | head down, body sinks | `blink 0.3, lookY -0.6, smile -0.8, headPitch 0.26, squash -0.09` |
| Surprised | wide | small round open | head back, body stretches | `eyeWide 1, mouthOpen 0.7, smile 0, headPitch -0.12, squash 0.08` |
| Thinking | look up and to one side | flat | tilt, a hand near the chin | `lookX -0.65, lookY 0.7, smile 0.1, headRoll 0.15, headYaw -0.2` |
| Confused | look to one side | flat or slightly down | strong tilt, lean back | `lookX 0.5, smile -0.15, headRoll -0.22, lean 0.05, eyeWide 0.2` |
| Excited | wide | open smile | arms up, body stretches | `eyeWide 0.5, mouthOpen 0.9, smile 1, armLRaise 1.7, armRRaise 1.7, squash 0.1` |

The template has clips for happy (wave), sad, thinking and excited (celebrate). If the user needs surprised or confused as animations, add them as clips in step 6 from these values.
