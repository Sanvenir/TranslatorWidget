A sample toolkit design for Paper reading. Translate
from English to Chinese 

![Toolkit pic](./toolkit.png)

# Instruction
Simple interface.

When you copy some English text the toolkit will translate
to Chinese.

Linebreaks in the paragraphs will be replaced by space.

The Window always on the top.

# Get started
You need to apply a [YouDao translator instance](https://ai.youdao.com/gw.s)
 before start. Reach your application ID and secret key, and fill them into following 
 json file under the root directory:

```json
{
  "APP_KEY": "Your app ID",
  "APP_SECRET": "Your secret key"
}
```

run
``
python main.py
``
to enter the main program.