# Scanned/Image Form Interaction

The scanned-form editor is mobile-first.

1. Single tap remains normal document interaction.
2. Double tap explicitly starts field creation at that location.
3. A default field rectangle is created.
4. The user selects Text, Checkbox, or Signature.
5. The frontend provides large touch-friendly handles for moving/resizing.
6. The frontend converts the final rectangle to normalized coordinates (0..1).
7. The backend stores the mapping.

The backend does not depend on mouse, touch, browser, or Tkinter events. It only receives the resulting normalized mapping.
