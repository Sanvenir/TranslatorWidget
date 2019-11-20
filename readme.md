A sample toolkit design for Paper reading. Translate
from English to Chinese 

![Toolkit pic](./toolkit.png)

# Instruction
Implement by PySide2, and use google translator with [Googletrans](https://py-googletrans.readthedocs.io/en/latest/).

When you copy some English text the toolkit will translate
to Chinese. And it can show the detail explanation of single word.

Can easily extend to other languages and other translator platform.

Linebreaks in the paragraphs will be replaced by space.
Especially, for source code of python, the "#"s in its documents will
also be ignored.

The Window can be set to always on top and can be dragged for convenience.

# Get Started
Using Python 3.x. Pre requirements list in requirements.txt.
You can set your configuration in ``config.json``
The parameters of json file:
- service_urls: A list of url of google translator api, [translate.google.cn](translate.google.cn) for common use;
- native: The native language of the user, text will be translated into this language;
- target: If the text is 
Run
``
python main.py
``
to enter the main program.

# How to Use
When you copy some text, the translation will show and be selected automatically on the left-top of 
your screen. You can copy this text, and you can also click the text once to cancel copy.
By default settings, the widget will move to corner to avoid your cursor.

An icon will be shown in your task panel, and you can adjust some setting 
in the right-clicked menu.
Toggle "Show Interface" on the left-bottom bar will also show some simple 
settings.
While the interface is enabled, you can drag to adjust the horizontal position of this widget.

- Check box "Clip" or "Enable clipboard translation" decides whether the widget receive copy text in the clipboard.
- Check box "Top" or "Always on top" decides whether the widget is always on the top.
- "Move to avoid mouse" means whether the widget move to corner when the cursor moves into the text area.
- Slider decides the opacity of the interface frame.
- Button "Clear" can clear the content of left-top translation.
