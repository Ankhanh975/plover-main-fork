from plover.formatting import Case, apply_case


def meta_case(ctx, case):
    case = Case(case.lower())
    action = ctx.copy_last_action()
    if not ctx.previous_translations and not ctx.translated_actions:
        action.next_attach = True
    action.next_case = case
    return action


def meta_retro_case(ctx, case):
    action = ctx.copy_last_action()
    action.prev_attach = True
    if case.lower() != "toggle_first_char":
        last_words = ctx.last_words(count=1)
        if last_words:
            action.prev_replace = last_words[0]
            action.text = apply_case(last_words[0], Case(case.lower()))
        else:
            action.text = ""
        return action

    last_word_parts = []
    found_word = False
    for word in ctx.iter_last_words():
        last_word_parts.append(word)
        if any(character.isalnum() or character == "_" for character in word):
            found_word = True
            break
    if found_word:
        last_word = "".join(reversed(last_word_parts))
    elif last_word_parts:
        last_word = last_word_parts[0]
    else:
        action.text = ""
        return action

    action.prev_replace = last_word
    index = next(
        (i for i, character in enumerate(last_word) if character.isalpha()), None
    )
    if index is None:
        action.text = last_word
    else:
        character = last_word[index]
        changed = character.lower() if character.isupper() else character.upper()
        action.text = last_word[:index] + changed + last_word[index + 1 :]
    return action
