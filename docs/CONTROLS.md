# Controls / Kontroller

The launcher stores keyboard and SDL gamepad mappings. The on-screen help follows the last input device and the mapped action. Use F1 to show/hide help. Face-button names vary by Xbox, PlayStation and Nintendo layout.

## Menus and long text

- Select: left stick / D-pad / arrows / WASD.
- Confirm: mapped south face button or Enter; RT also confirms a selected menu item.
- Back / cancel: mapped east face button or Escape. Start pauses/resumes.
- Long story, help and history text: right-stick Y, mouse wheel, Page Up / Page Down.
- Move over a button with the mouse or select it with the controller to change its color. Selection uses a tint rather than an outline box.
- Held axes must return to neutral after a new menu / loading screen; they do not immediately change the default selection.

## Death and retry

The right-hand Retry item is the default on a failure result. Press confirm or release and press RT again. An early result confirmation is queued briefly until the result animation is ready. Holding fire through death does not automatically restart. The following advice / Ready screens also accept confirmation.

## Mission 18 — Screaming Mantis

Shoot the useful doll down and pick it up using the original game rules. While it is equipped (weapon mode 6), the game expects a phone shake. The desktop version shows an animated R-stick prompt: **move the right stick left and right**. A real direction reversal triggers the original shake animation. Holding one side does not. The shake action is also available through the configured shake key (default F) or mapped shake button.

Damage timing and the boss taking the doll back are original game behavior. This integration does not force boss damage or suppress the takeover timer.

## Mission 20 — Liquid

**Mission 20 only:** push the right stick decisively left or right to perform the corresponding screen-relative dodge. Centre it before another dodge. Horizontal input must dominate the vertical axis. Holding a direction does not repeat, and held input is ignored after loading or resuming until the stick is centred.

The desktop action calls the original game's flick path. Dodge animation, recovery timing and protection are the game's own. The final landscape mapping was corrected in 1.0.7.

## Post-game advice

The Survival unlock advice uses its own scene (13). Since 1.0.8 it is treated as landscape and exposes the original **Next / İleri** target to the common controller/keyboard menu path. Confirmation releases the original advice textures and proceeds normally.
