# Knowledge Brain

Knowledge Brain is a small place to keep notes that should last.

## What knowledge-brain Is

`knowledge-brain` saves useful notes for later.

You can think of it as a notebook for an AI tool or a project.
It keeps facts, decisions, and reminders in a file on your machine so they do not disappear when a session ends.

## Why Memory Is Separate From The Runtime

Memory is kept separate from the running tool so the notes survive even when the tool closes, restarts, or changes.

This also makes it easier to share the same notes across different tools without tying them to one specific session.

## Two Kinds Of Memory

There are two main ways to use memory here:

- project-local memory: notes for one project only
- global memory: notes that can be used across many projects

The difference is where the notes are stored.

## The Safe Default

The safe default is project-local memory.

That means new notes stay with the project unless you choose to store them somewhere else.
This helps keep project work separate and reduces accidental sharing.

## Tiny Example

```bash
brain init
brain write "This project uses project-local memory by default." --tags project,example
brain query "project-local memory"
```

`brain init` creates the local note file for this project.
`brain write` saves one note with two tags: `project` and `example`.
`brain query` looks up notes that mention "project-local memory".

Expected result: the note is saved, and the query returns that note from the project-local store.

## How It Connects To context_os

`context_os` can use Knowledge Brain as its long-term note store.

In simple terms, `context_os` can point to a project-specific note file when memory should stay with one repo, or to a shared note file when memory should follow you across projects.

## When To Use Global Memory

Use global memory for notes that are personal and useful almost everywhere.

Good examples:
- your preferred coding style
- machine setup notes
- facts you want available in every project

## When Not To Use Global Memory

Do not use global memory for things that belong to only one project.

Avoid it for:
- temporary ideas
- implementation details for one repo
- decisions that may change soon
- anything you would not want mixed into unrelated work
