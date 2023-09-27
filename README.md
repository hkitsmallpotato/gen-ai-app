# gen-ai-app

*TODO*: Applications enabled by LLM

## auto-ai-miniapp

What if we use LLM... to engineer LLM based applications?

More recent LLM such as llama2 can roleplay a pretty reasonable prompt engineer, and some *low grade* LLM enabled applications are fairly feasible to be auto-engineered by them.

By LLM enabled applications I mean things that are possible when backed by a general purpose LLM as an AI core, with some helper codes surrounding it allowed. (TODO: link to that training slide)

By *low grade* I mean those use case that rely on relatively *easy* (not to look down on them) domain and didn't hit one of the LLM's weak spots. So marketing copy editor yes, full fledged programmer no.

In these case *automation* is actually possible too, as well as a more interactive, chat based approach. For automation we can use simple prompt-chaining.

### Workflow

1. User specify topic plus instruction/requirements. If no idea, can also choose a broad domain and let AI generate app idea.
2. AI design prompts and examples, and then auto-extarct/format it into a machine readable format, something like an *Application definition*. Here we use JSON.
3. User can test drive the app by "Deploying" it live, and then do a sample run.

### Application definition

Currently it includes the following:

- `meta`: General info like app name, description, and the main text prompt.
- `ui`: Programmatic UI layout for a simple form with (dynamic) fields so that user can input info more flexibly.
- `eg`: A set of AI generated example inputs data. This allow end user to get started quickly.
- `chain`: Simple prompt chains with a set of followup questions that AI can automatically generate answers to in batch mode.
