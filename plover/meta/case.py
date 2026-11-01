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
    last_words = ctx.last_words(count=1)
    if last_words:
        action.prev_replace = last_words[0]
        if case.lower() == "toggle_first_char":
            word = last_words[0]
            index = next(
                (i for i, character in enumerate(word) if character.isalpha()), None
            )
            if index is None:
                action.text = word
            else:
                character = word[index]
                changed = (
                    character.lower() if character.isupper() else character.upper()
                )
                action.text = word[:index] + changed + word[index + 1 :]
        else:
            action.text = apply_case(last_words[0], Case(case.lower()))
    else:
        action.text = ""
    return action
