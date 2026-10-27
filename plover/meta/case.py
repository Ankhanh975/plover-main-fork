from plover.formatting import (
    Case,
    apply_case,
    capitalize_first_word,
    lower_first_character,
)


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
            action.text = (
                lower_first_character(word)
                if word[0:1].isupper()
                else capitalize_first_word(word)
            )
        else:
            action.text = apply_case(last_words[0], Case(case.lower()))
    else:
        action.text = ""
    return action
