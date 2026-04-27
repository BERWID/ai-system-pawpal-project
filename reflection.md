# PawPal+ Project Reflection AINExtension

## 1. How I used AI

**a. Initial design**

I used claude and gemini throughout this project. claude helped me design the structure of the ai_helper.py file and create the input validation guardrail. gemini is integrated as the AI assistant inside the app itself.

One helpful suggestion claude made was separating the ai logic into its own ai_helper.py module rather than mixing it into app.py. This had made the code much easier to test and reason about.

One flawed suggestion claude made was suggested adding a complex multi-turn conversation loop to the gemini calls. That was unnecessary,single-turn prompts work fine here and are simpler to debug.

---

## 2. System Limitations

1. no persistent storage.
2. The guardrail blocks known bad terms but can't catch all unsafe inputs.

---

## 3. Future Improvements

Store tasks in a database so they persist across sessions.
Let the owner rate the AI advice and use that to improve future prompts.

