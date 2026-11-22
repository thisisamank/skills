# Handoff: step 8

Give these only when the user asks. Ask which target they need (web, Blender, Unity) and give that part, not all of it.

## Contents
1. Which page file to use
2. GLB with baked animations
3. Blender: bones, shape keys, keyframed actions
4. Plain Three.js
5. React
6. Unity
7. App events to animations
8. A model from an artist or an image-to-3D tool
9. What was tested

## 1. Which page file to use

| File | Has | Use for |
|---|---|---|
| `<name>-mascot.html` (before `inline`) | three.js from the CDN, so add-ons can load | GLB export, more edits |
| `<name>-preview.html` (after `inline`) | three.js inside, no network | sharing, rig export |

Add `?handoff` to the address of the first file to show two buttons: "Download GLB" and "Download rig JSON". The user can do the export without a terminal.

## 2. GLB with baked animations

```bash
python3 scripts/mascot_tools.py glb <name>-mascot.html <name>.glb
```

This needs a Chrome-family browser and a network. Without them, tell the user to open `<name>-mascot.html?handoff` and press "Download GLB".

The export code is in the page, in the HANDOFF part. Show it to the user if they ask for "the GLB export code":

- `bakeClips()` plays each clip at 24 frames per second with `mascot.sample`, and records position, rotation, scale and morph weights of every node. It makes one `THREE.AnimationClip` for each clip and drops tracks that do not change.
- `exportGLB()` gives the mascot root and those clips to `GLTFExporter` from `three/addons/exporters/GLTFExporter.js` with `{ binary: true, animations }`.

What the file contains, so the user knows what to expect:
- One node for each part, animated by node transforms. There is no skin. This is correct for a mascot made of rigid parts, and every engine reads it.
- The mouth has one morph target, `smile`.
- Animation names are the clip names: `idle`, `wave`, `celebrate`, `thinking`, `sad`, `point`, `talk`.
- Loop clips have the same first and last frame. The idle has one blink. Pointer follow and random blinks are live behavior, so they are not in the file. The engine must add them (see Unity below).
- glTF has no toon material. A toon mascot exports with the clay material.
- Colors are fixed at export time. Set them first.

## 3. Blender: bones, shape keys, keyframed actions

Two commands:

```bash
python3 scripts/mascot_tools.py rig <name>-preview.html <name>-rig.json
blender --background --python scripts/rebuild_in_blender.py -- <name>-rig.json --blend <name>.blend --glb <name>-skinned.glb --verify
```

Give the user `rebuild_in_blender.py` and the rig JSON. If Blender is not on this machine, the user runs the second command. They can also open the script in Blender's Scripting tab, set `RIG_JSON` at the top, and press Run. In that case the script adds a new collection and leaves their scene alone.

The script is general. It reads the rig JSON, so it works for any mascot built from the template with no edits. It makes:

- An armature with one bone for each `bone()` in the page (`root`, `hips`, `head`, `armL`, `armR`, `antenna`, and any you added).
- One mesh with a vertex group for each bone (each part follows one bone fully), an Armature modifier, and a material for each color slot.
- A shape key for each face channel that changes the mesh: `blink`, `eyeWide`, `lookX`, `lookY`, `mouthOpen`, `smile`.
- Two actions for each clip: `wave` on the armature and `wave_face` on the shape keys, keyed on every frame at 24 fps. Each pair is also on a muted NLA track with the clip name. The glTF exporter merges the two tracks into one animation.

`--verify` plays some frames of every clip in Blender and compares part positions with the positions the page recorded. Bones must match within 0.002 units. Face parts get 0.05, because a shape key is a straight-line version of a small turn.

Limits to state:
- Spring parts (antenna, ears) are baked as keyframes. In Blender they do not react to new motion.
- Shape keys add up in straight lines. The page multiplies some of them (for example the smile fades when the mouth opens). Faces in Blender can differ slightly from the page.
- A bone that the page scales must have no turn in its rest pose. The template scales only `hips`.

## 4. Plain Three.js

```bash
python3 scripts/mascot_tools.py module <name>-mascot.html mascot.js
```

`mascot.js` exports `createMascot(THREE, options)`. The user needs `three` at version 0.160 or later.

```js
import * as THREE from 'three';
import { createMascot } from './mascot.js';

const mascot = createMascot(THREE, { personality: 'friendly', colors: { body: '#6d5efc' } });
const holder = new THREE.Group();          // move and scale the holder. The clips own the root's height and turn.
holder.add(mascot.root);                   // the mascot is about 2 units tall, feet at y = 0, facing +Z
holder.scale.setScalar(0.5);
scene.add(holder);

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => { mascot.update(clock.getDelta()); renderer.render(scene, camera); });

// eyes follow the pointer: x and y from -1 to 1, relative to the mascot on screen
window.addEventListener('pointermove', e => {
  const r = renderer.domElement.getBoundingClientRect();
  mascot.lookAt((e.clientX - (r.left + r.width / 2)) / (r.height / 2), -(e.clientY - (r.top + r.height / 3)) / (r.height / 2));
});
```

The scene needs light. For the glossy toy material, also copy `studioEnvironment()` from the page and set `scene.environment`, or the gloss has nothing to reflect.

## 5. React

```jsx
// Mascot.jsx
import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import * as THREE from 'three';
import { createMascot } from './mascot.js';

export const Mascot = forwardRef(function Mascot({ state = 'idle', size = 240, options }, ref) {
  const canvasRef = useRef(null);
  const mascotRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(size, size, false);
    renderer.toneMapping = THREE.NeutralToneMapping;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(28, 1, 0.1, 60);
    camera.position.set(0, 1.4, 6.9);
    camera.lookAt(0, 1.3, 0);
    scene.add(new THREE.HemisphereLight(0xffffff, 0xd9d4ee, 1.6));
    const key = new THREE.DirectionalLight(0xffffff, 2);
    key.position.set(-3, 6.5, 5);
    scene.add(key);

    const mascot = createMascot(THREE, options);
    scene.add(mascot.root);
    mascotRef.current = mascot;

    const onMove = (e) => {
      const r = canvas.getBoundingClientRect();
      mascot.lookAt((e.clientX - (r.left + r.width / 2)) / 300, -(e.clientY - (r.top + r.height / 3)) / 300);
    };
    window.addEventListener('pointermove', onMove);

    let raf = 0, last = performance.now();
    const frame = (now) => {
      mascot.update((now - last) / 1000);
      last = now;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => { cancelAnimationFrame(raf); window.removeEventListener('pointermove', onMove); renderer.dispose(); mascotRef.current = null; };
  }, [size, options]);

  useEffect(() => { mascotRef.current?.play(state); }, [state]);
  useImperativeHandle(ref, () => ({ play: (name, o) => mascotRef.current?.play(name, o), stop: () => mascotRef.current?.stop() }), []);

  return <canvas ref={canvasRef} style={{ width: size, height: size }} aria-hidden="true" />;
});
```

Use it in two ways. Loop states come from data: `<Mascot state={isLoading ? 'thinking' : 'idle'} />`. One-shot moves come from events: `mascotRef.current.play('celebrate')` in the success handler. Tell the user to keep `options` stable (a constant or `useMemo`), or the effect builds the mascot again on each render.

In Next.js, the file needs `'use client'`, because it uses WebGL.

## 6. Unity

1. Import the GLB. Unity does not read GLB by default. Add the glTFast package (`com.unity.cloud.gltfast`), or export FBX from the Blender file.
2. Make an Animator Controller with one state for each clip. Give each state the clip name. Set Loop Time on `idle`, `thinking` and `talk`. Do not add transitions. The script cross-fades.
3. Put this script on the mascot root.

```csharp
using UnityEngine;

[RequireComponent(typeof(Animator))]
public class MascotController : MonoBehaviour
{
    [SerializeField] float blend = 0.28f;        // seconds. Use the personality's blend time.
    [SerializeField] Transform head;             // the head node, for the pointer follow
    [SerializeField, Range(0f, 1f)] float follow = 0.6f;

    static readonly string[] Loops = { "idle", "thinking", "talk" };
    Animator animator;
    string current = "idle";
    Vector2 look;

    void Awake() { animator = GetComponent<Animator>(); }

    public void Play(string clip)
    {
        current = clip;
        animator.CrossFadeInFixedTime(clip, blend);
    }

    public void Stop() { Play("idle"); }

    void Update()
    {
        // a one-shot clip returns to idle when it ends
        if (System.Array.IndexOf(Loops, current) >= 0 || animator.IsInTransition(0)) return;
        var info = animator.GetCurrentAnimatorStateInfo(0);
        if (info.IsName(current) && info.normalizedTime >= 1f) Play("idle");
    }

    void LateUpdate()   // after the Animator, so the turn adds to the clip
    {
        if (head == null) return;
        var m = new Vector2(Input.mousePosition.x / Screen.width - 0.5f, Input.mousePosition.y / Screen.height - 0.5f) * 2f;
        look = Vector2.Lerp(look, m, 1f - Mathf.Exp(-Time.deltaTime * 5f));
        head.localRotation *= Quaternion.Euler(-look.y * 12f * follow, look.x * 18f * follow, 0f);
    }
}
```

Call it from game code: `mascot.Play("celebrate")`. If the head turns the wrong way, change the signs in the last line. The axes depend on the importer. With the new Input System, read the pointer from `Mouse.current.position.ReadValue()`.

## 7. App events to animations

Give the user a table like this, changed for their product. It is the contract between the app and the mascot.

| App event | Call | Note |
|---|---|---|
| First visit, page load | `play('wave')` | One time for each session, not on every navigation |
| Request or job starts | `play('thinking')` | It loops. Call `stop()` when the result arrives. |
| Success, goal reached, purchase done | `play('celebrate')` | Keep it for real wins, or it loses its effect |
| Error, failed validation | `play('sad')` | Short. Show the error text at the same time. |
| Tip, onboarding step, new feature | `play('point')` or `play('point', { mirror: true })` | Point toward the UI element |
| The mascot "says" something | `play('talk')`, then `stop()` | Stop when the text or the audio ends |
| Nothing happens | idle | The default. Eyes follow the pointer. |

Rules to give with it: one animation for one event, never start a loud animation without a user action, and respect the system "reduce motion" setting.

## 8. A model from an artist or an image-to-3D tool

When the character is too detailed for primitives, the model comes from elsewhere as a GLB. This skill then does the rest.

- Rigging: ask for (or make in Blender) bones with the same names as the template: `root`, `hips`, `head`, `armL`, `armR`, and face shape keys `blink`, `smile`, `mouthOpen`.
- Animation logic: if the GLB has its own clips, play them with a mixer and the same state rules:

```js
const mixer = new THREE.AnimationMixer(gltf.scene);
const actions = Object.fromEntries(gltf.animations.map(c => [c.name, mixer.clipAction(c)]));
const LOOPS = new Set(['idle', 'thinking', 'talk']);
let current = actions.idle.play();

function play(name, fade = 0.28) {
  const next = actions[name];
  if (!next || next === current) return;
  next.reset();
  next.setLoop(LOOPS.has(name) ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
  next.clampWhenFinished = true;
  next.crossFadeFrom(current, fade, false).play();
  current = next;
}
mixer.addEventListener('finished', () => play('idle'));     // a one-shot returns to idle
// each frame: mixer.update(dt)
```

- If the GLB has bones but no clips, keep the pose system from the template: replace the body of `applyPose` so that it writes the channels to the loaded bones and morph targets. The clips, the state machine, the blink and the pointer follow then work as before.
- Integration: sections 4 to 7 apply without change.

The same mixer code plays the GLB from section 2, for a site that wants the file and not the code module.

## 9. What was tested

Say this to the user when you hand over. Do not claim more.

- Tested with the template mascot: the GLB export (opened in Blender 5.3, 7 animations), the rig export, and `rebuild_in_blender.py` with `--verify` in Blender 4.2 LTS and 5.3.
- Not run: the React component and the Unity script. They are a start. Run them in the user's project and fix what the project needs.
- After you change the shape or the clips, run `--verify` again if Blender is available.
