# %% [markdown]
# ## 🎓 𝗗𝗦𝗣: 𝗗emonstrate–𝗦earch–𝗣redict
# 
# This notebook illustrates the Demonstrate–Search–Predict (𝗗𝗦𝗣) framework on the multi-hop question answering (QA) task.
# 
# Below, we'll build **five** small 𝗗𝗦𝗣 programs that implement strategies for this task. The programs range from extremely simple ones (programs 1 and 2) to moderate ones (programs 3 and 4). Program 5 considers a fairly advanced pipeline.

# %% [markdown]
# ### Installation
# 
# If you haven't installed **DSP** already, let's do that.

# %%
# try: # When on google Colab, let's clone the notebook so we download the cache.
#     import google.colab 
#     !git -C dsp/ pull || git clone https://github.com/stanfordnlp/dsp
# except: pass

# !pip install -U pip dsp-ml

# %% [markdown]
# ### Setting Up
# 
# We'll start by setting up the language model (LM) and retrieval model (RM).
# 
# We will work with the **GPT-3.5** LM (`text-davinci-002`) and the **ColBERTv2** RM.
# 
# To use GPT-3, you'll need an OpenAI key. For ColBERTv2, we've set up a server hosting a Wikipedia (Dec 2018) search index, so you don't need to worry about setting one up!
# 
# To make things easy, we've set up a cache in this repository. _If you want to run this notebook without changing the code or examples, you don't need an API key. All examples are cached._

# %%
# %load_ext autoreload
# %autoreload 2

try: import google.colab; root_path = 'dsp'
except: root_path = '.'

import os
os.environ["DSP_NOTEBOOK_CACHEDIR"] = os.path.join(root_path, 'cache')

import dsp

openai_key = os.getenv('OPENAI_API_KEY')  # or replace with your API key (optional)
colbert_server = 'http://ec2-44-228-128-229.us-west-2.compute.amazonaws.com:8893/api/search'

lm = dsp.GPT3(model='text-davinci-002', api_key=openai_key)
rm = dsp.ColBERTv2(url=colbert_server)

dsp.settings.configure(lm=lm, rm=rm)

# %% [markdown]
# ### Task Examples
# 
# Next, let's look at a few examples of the task. Each example consists of a question and one or more gold answers.
# 
# We have six training examples (`train`), which we'll feed into the programs. These will help define the task.
# 
# Notice that our examples only have input (`question`) and output (`answer`) fields. When our advanced programs build sophisticated pipelines, training "demonstrations" for other fields will be constructed automatically.

# %%
train = [('Who produced the album that included a re-recording of "Lithium"?', ['Butch Vig']),
         ('Who was the director of the 2009 movie featuring Peter Outerbridge as William Easton?', ['Kevin Greutert']),
         ('The heir to the Du Pont family fortune sponsored what wrestling team?', ['Foxcatcher', 'Team Foxcatcher', 'Foxcatcher Team']),
         ('In what year was the star of To Hell and Back born?', ['1925']),
         ('Which award did the first book of Gary Zukav receive?', ['U.S. National Book Award', 'National Book Award']),
         ('What city was the victim of Joseph Druces working in?', ['Boston, Massachusetts', 'Boston']),]

train = [dsp.Example(question=question, answer=answer) for question, answer in train]

# %% [markdown]
# The development examples (`dev`) will be used to assess the behavior of each program we build. Of course, this tiny set is not meant to be a reliable benchmark, but it'll be instructive to use it for illustration.

# %%
dev = [('Who has a broader scope of profession: E. L. Doctorow or Julia Peterkin?', ['E. L. Doctorow', 'E.L. Doctorow', 'Doctorow']),
       ('What documentary about the Gilgo Beach Killer debuted on A&E?', ['The Killing Season']),
       ('Right Back At It Again contains lyrics co-written by the singer born in what city?', ['Gainesville, Florida', 'Gainesville']),
       ('What year was the party of the winner of the 1971 San Francisco mayoral election founded?', ['1828']),
       ('Which author is English: John Braine or Studs Terkel?', ['John Braine']),
       ('Anthony Dirrell is the brother of which super middleweight title holder?', ['Andre Dirrell']),
       ('In which city is the sports nutrition business established by Oliver Cookson based ?', ['Cheshire', 'Cheshire, UK']),
       ('Find the birth date of the actor who played roles in First Wives Club and Searching for the Elephant.', ['February 13, 1980']),
       ('Kyle Moran was born in the town on what river?', ['Castletown', 'Castletown River']),
       ("What is the name of one branch of Robert D. Braun's speciality?", ['aeronautical engineering', 'astronautical engineering', 'aeronautics', 'astronautics']),
       ("Where was the actress who played the niece in the Priest film born?", ['Surrey', 'Guildford, Surrey']),
       ('Name the movie in which the daughter of Noel Harrison plays Violet Trefusis.', ['Portrait of a Marriage']),
       ('What year was the father of the Princes in the Tower born?', ['1442'])]

dev = [dsp.Example(question=question, answer=answer) for question, answer in dev]

# %% [markdown]
# ### Program 1: Vanilla GPT-3.5
# 
# Let's begin by implementing the simplest program for this task. We'll prompt **GPT-3.5** to answer each question based on its internal parameteric knowledge.
# 
# We'll start by defining the `Template` that defines how we will communicate with the LM.
# 
# Specifically, the question–answer template (`qa_template`) will include a question and a short answer for each example.

# %%
Question = dsp.Type(prefix="Question:", desc="${the question to be answered}")
Answer = dsp.Type(prefix="Answer:", desc="${a short factoid answer, often between 1 and 5 words}", format=dsp.format_answers)

qa_template = dsp.Template(instructions="Answer questions with short factoid answers.", question=Question(), answer=Answer())

# %% [markdown]
# Then, let's define the actual program, `vanilla_LM_QA`. It'll accept a string (`question`) and returns another string (its short `answer`).

# %%
def vanilla_LM_QA(question: str) -> str:
    demos = dsp.sample(train, k=7)
    example = dsp.Example(question=question, demos=demos)

    example, completions = dsp.generate(qa_template)(example, stage='qa')
    return completions.answer

# %% [markdown]
# Let's invoke the program on a sample question.

# %%
print(dev[0].question)
print(vanilla_LM_QA(dev[0].question))

# %% [markdown]
# Let's inspect the last call to the LM to learn more about the behavior of the program.

# %%
lm.inspect_history(n=1)

# %% [markdown]
# We can see that the program has organized the examples in a simple prompt and generated an answer for the `dev[0]` question we asked.
# 
# Let's try on the remaining development examples.

# %%
from dsp.evaluation.utils import evaluate

evaluate(vanilla_LM_QA, dev)

exit()
# %% [markdown]
# ### Program 2: Retrieve-then-Read w/ GPT-3.5
# 
# The program above relies entirely on the factual knowledge memorized by GPT-3. As we have seen, it's sometimes correct but it's far from reliable.
# 
# Let's try to address this. Our first improvement to the vanilla **GPT-3.5** strategy is to include search results in the LM prompt, often called a *retrieve-then-read* approach.
# 
# In particular, we'll retrieve the most relevant passage to the question (according to the retriever) from the corpus and concatenate it into the prompt. This may help GPT-3.5 answer more factually.
# 
# To do this, we'll need to modify the `Template`. In particular, we'll define a `qa_template_with_passages` template, which will include a `context` field in addition to a question and an answer.

# %%
Context = dsp.Type(
    prefix="Context:\n",
    desc="${sources that may contain relevant content}",
    format=dsp.passages2text
)

qa_template_with_passages = dsp.Template(
    instructions=qa_template.instructions,
    context=Context(), question=Question(), answer=Answer()
)

# %% [markdown]
# Now let's modify the program. We'll call `dsp.retrieve`, which we hooked earlier in this notebook to a **ColBERTv2** retriever serving a Wikipedia (Dec 2018) index.

# %%
def retrieve_then_read_QA(question: str) -> str:
    demos = dsp.sample(train, k=7)
    passages = dsp.retrieve(question, k=1)
    
    example = dsp.Example(question=question, context=passages, demos=demos)
    example, completions = dsp.generate(qa_template_with_passages)(example, stage='qa')

    return completions.answer

# %% [markdown]
# Let's invoke this on a sample question and let's inspect the last call to the LM to learn more about the behavior of the program.

# %%
retrieve_then_read_QA(dev[0].question), lm.inspect_history(n=1)

# %% [markdown]
# Now, let's evaluate this on the dev examples.

# %%
evaluate(retrieve_then_read_QA, dev)

# %% [markdown]
# ### Program 3: Retrieve-then-Read w/ Self-Consistency
# 
# It's clear that retrieval has the capacity to help **GPT-3.5** answer a larger number of questions more factually. However, these questions are too complicated for a single retrieved passage to suffice.
# 
# In this program, we try to make some improvements to the pipeline from **Program 2**.
# 
# In particular:
# 
# - We will include 5 passages (instead of a single passage) into the prompt.
# - We will ask GPT-3.5 to generate a Chain-of-Thought (CoT) rationale to more effectively extract the answer from the passages.
# - We will use Self-Consistency (SC) to marginalize this prediction across many chains of thought.

# %%
Rationale = dsp.Type(
    prefix="Rationale: Let's think step by step.",
    desc="${a step-by-step deduction that identifies the correct response, which will be provided below}"
)

qa_template_with_CoT = dsp.Template(
    instructions=qa_template.instructions,
    context=Context(), question=Question(), rationale=Rationale(), answer=Answer()
)

# %% [markdown]
# The snippet above updates our template to include a `rationale` field.
# 
# Below, we define the new program `retrieve_then_read_QA_v2`. In it, we define a new DSP _transformation_ `QA_predict`, which we will re-use in multiple programs.
# 
# The transformation `QA_predict` takes an `Example` (which has a question, context, and demonstrations) and generates an answer. It can be configured to use self-consistency (`sc=True`) or not.

# %%
@dsp.transformation
def QA_predict(example: dsp.Example, sc=True):
    if sc:
        example, completions = dsp.generate(qa_template_with_CoT, n=20, temperature=0.7)(example, stage='qa')
        completions = dsp.majority(completions)
    else:
        example, completions = dsp.generate(qa_template_with_CoT)(example, stage='qa')
    
    return example.copy(answer=completions.answer)

def retrieve_then_read_QA_v2(question: str) -> str:
    demos = dsp.sample(train, k=7)
    passages = dsp.retrieve(question, k=5)
    example = dsp.Example(question=question, context=passages, demos=demos)
    
    return QA_predict(example).answer

# %% [markdown]
# Let's inspect an example.

# %%
retrieve_then_read_QA_v2(dev[2].question), lm.inspect_history(n=1)

# %% [markdown]
# And let's run this on the other dev examples.

# %%
evaluate(retrieve_then_read_QA_v2, dev)

# %% [markdown]
# ### Program 4: Multi-Hop Retrieval
# 
# From these simple programs, it becomes clear that a single search query is not enough for this task. This can be seen when trying to find the birth city of the writer of "Right Back At It Again". A search query identifies the author correctly as "Jeremy McKinnon", but it doesn't mention when he was born.
# 
# The standard approach for this challenge in the retrieval-augmented NLP literature is to build multi-hop search systems, like GoldEn (Qi et al., 2019), IRRR (Qi et al., 2021) and Baleen (Khattab et al., 2021). These systems read the retrieved results and then generate additional queries to gather additional information if necessary.

# %% [markdown]
# 
# With **DSP**, we can easily simulate such systems in a few lines of code. Let's begin by defining two new templates.
# 
# First, in `rewrite_template`, we will re-write the input question into a simple search query. This will serve as our "first hop" query.

# %%
SearchRationale = dsp.Type(
    prefix="Rationale: Let's think step by step. To answer this question, we first need to find out",
    desc="${the missing information}"
)

SearchQuery = dsp.Type(
    prefix="Search Query:",
    desc="${a simple question for seeking the missing information}"
)

rewrite_template = dsp.Template(
    instructions="Write a search query that will help answer a complex question.",
    question=Question(), rationale=SearchRationale(), query=SearchQuery()
)

# %% [markdown]
# Next, in `hop_template`, we will use the retrieved information from earlier hops to generate additional search queries for missing information.

# %%
CondenseRationale = dsp.Type(
    prefix="Rationale: Let's think step by step. Based on the context, we have learned the following.",
    desc="${information from the context that provides useful clues}"
)

hop_template = dsp.Template(
    instructions=rewrite_template.instructions,
    context=Context(), question=Question(), rationale=CondenseRationale(), query=SearchQuery()
)

# %% [markdown]
# Let's build our `multihop_QA_v1` program. The hallmark of this program is the search transformation called `multihop_search_v1`.
# 
# This will largely simulate the IRRR system. In each hop, we will retrieve `k` (e.g., `k=2`) passages and concatenate them to the context retrieved from earlier hops to form a `context` chain.
# 
# For simplicity, we will repeat this for a total of `max_hops` hops (e.g., `max_hops=2`). It's easy to add a stopping criteria in which the LM is asked whether more hops are required.

# %%
from dsp.utils import deduplicate

@dsp.transformation
def multihop_search_v1(example: dsp.Example, max_hops=2, k=2) -> dsp.Example:
    example.context = []
    
    for hop in range(max_hops):
        # Generate a query based
        template = rewrite_template if hop == 0 else hop_template
        example, completions = dsp.generate(template)(example, stage=f'h{hop}')

        # Retrieve k results based on the query generated
        passages = dsp.retrieve(completions.query, k=k)

        # Update the context by concatenating old and new passages
        example.context = deduplicate(example.context + passages)

    return example


def multihop_QA_v1(question: str) -> str:
    demos = dsp.sample(train, k=7)
    x = dsp.Example(question=question, demos=demos)
    
    x = multihop_search_v1(x)
    x = QA_predict(x, sc=False)

    return x.answer

# %% [markdown]
# Let's run this on one example and inspect the last 3 calls to the LM (i.e., search query 1, search query 2, and QA).

# %%
multihop_QA_v1(dev[2].question), lm.inspect_history(n=3)

# %% [markdown]
# Now, let's run this on the remaining dev examples.

# %%
evaluate(multihop_QA_v1, dev)

# %% [markdown]
# ### Program 5: Multi-Hop Condensed Retrieval w/ Automatic Demos and Query Fusion
# 
# Through Program 4, we've begun to explore some of the power of the DSP abstraction. However, if you look closely, you will see a few downsides of the previous approach:
# 
# 1. The search transformations invoke the LM without any demonstrations in the prompt. That is because we only have training data for the question–answer pairs and not for the intermediate labels (e.g., search queries).
# 2. The QA prompt uses passages (`context`) and a Chain-of-Thought (`rationale`) for the question to be answered. However, the training demonstrations include neither context nor CoT because they aren't available in our labels.
# 3. The search transformations commit to a single query per hop, which may single out an unproductive chain of passages and hence fail to uncover relevant information.

# %% [markdown]
# We address these problems automatically in the program below.
# 
# In it, we begin by defining `multihop_demonstrate` (which uses `multihop_attempt`) to automatically **annotate** demonstrations for the complex multi-hop pipeline. These demonstrations will be provided to the LM when it's invoked for each transformation.

# %%
@dsp.transformation
def multihop_attempt(d: dsp.Example) -> dsp.Example:
    # Prepare unaugmented demonstrations for the example.
    x = dsp.Example(question=d.question, demos=dsp.all_but(train, d))
    
    # Search. And skip examples where search fails.
    # Annotate demonstrations for multihop_search_v2 with the simpler multihop_search_v1 pipeline.
    x = multihop_search_v1(x)
    if not dsp.passage_match(x.context, d.answer): return None
    
    # Predict. And skip examples where predict fails.
    x = QA_predict(x, sc=False)
    if not dsp.answer_match(x.answer, d.answer): return None
    
    return d.copy(**x)

@dsp.transformation
def multihop_demonstrate(x: dsp.Example) -> dsp.Example:
    demos = dsp.sample(train, k=7)
    x.demos = dsp.annotate(multihop_attempt)(demos, k=3, return_all=True)
    return x

# %% [markdown]
# We now implement `multihop_search_v2` as part of `multihop_QA_v2`.
# 
# In addition to the changes mentioned earlier, this program simulates the Baleen system (Khattab et al., 2021) in a few lines of code.
# 
# In each retrieval hop (after the very first hop), the summary of the previous hop(s) is included in the prompt. This allows us to efficiently read a larger number of passages from the current hop.

# %%
@dsp.transformation
def multihop_search_v2(example: dsp.Example, max_hops=2, k=5) -> dsp.Example:
    example.context = []

    for hop in range(max_hops):
        # Generate queries
        template = rewrite_template if hop == 0 else hop_template
        example, completions = dsp.generate(template, n=10, temperature=0.7)(example, stage=f'h{hop}')
        
        # Collect the queries and search with result fusion
        queries = [c.query for c in completions] + [example.question]
        example.context = dsp.retrieveEnsemble(queries, k=k)

        # Arrange the passages for the next hop
        if hop > 0:
            example.context = [completions[0].rationale] + example.context
    
    return example

def multihop_QA_v2(question: str) -> str:
    x = dsp.Example(question=question)
    x = multihop_demonstrate(x)
    x = multihop_search_v2(x)
    x = QA_predict(x)
    return x.answer

# %%
multihop_QA_v2(dev[3].question), lm.inspect_history(n=3)

# %%
evaluate(multihop_QA_v2, dev)

# %% [markdown]
# ### Ask your own questions
# 
# You could also ask your own questions. This can be a productive vehicle to find problems in the programs above and implement patches for them! (Keep in mind that the search index we're using currently is from Dec 2018.)
# 
# To do this, make sure you set your API key. This can be done by defining the `OPENAI_API_KEY` environemt variable or setting it at the beginning of the program (Cell #2).

# %%
multihop_QA_v2("When was the creator of Hadoop given an award?"), lm.inspect_history(n=3)

# %% [markdown]
# ### Additional Programs...
# 
# While Program 5 is undeniably better than, say, Program 1, it's far from perfect.
# 
# Many different ideas can easily be implemented to make it more general or more powerful. Refer to the DSP paper for inspiration!
# 
# One of your first improvements to Programs 4 and 5 would be to allow it to do more than two hops and to automatically stop when additional hops are not required.
# 
# **Hint:** This is pretty easy to do. You can start with Program 4 and modify `hop_template` so its `SearchQuery` produces the string `N/A` when additional hops are not required.
# 
# In the `multihop_search_v1` function, you can then break from the loop — i.e., `if completions.query == 'N/A': break` whenever this happens. How will you apply this to Program 5?
# 
# ```
# SearchQueryWithStopping = dsp.Type(
#     prefix="Search Query:",
#     desc="${a simple question for seeking the missing or required information --- say N/A if the context above contains all of the required information}"
# )
# ```

# %% [markdown]
# Other incremental improvements will likely help program 5, including keeping the top passage from each hop in the context and/or the summary of each hop. To decide which changes to make, you can inspect the trace of the program when it makes mistakes!

# %%
# Program 4 with max_hops=4 and automatic stopping.


