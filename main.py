def define_env(env):
    @env.macro
    def show_readme(filename: str):
        with open(filename, "r") as file:
            content = file.read()
        return convert_admonitions(content)


def convert_admonitions(text: str) -> str:
    lines = text.splitlines()

    admonition = False
    indexes = []

    for i in range(len(lines)):
        if lines[i].startswith("> [!NOTE]"):
            admonition = True
            lines[i] = "!!! note"
            indexes.append(i + 1)
        elif lines[i].startswith("> [!TIP]"):
            admonition = True
            lines[i] = "!!! tip"
            indexes.append(i + 1)
        elif lines[i].startswith("> [!IMPORTANT]"):
            admonition = True
            lines[i] = '!!! info "Important"'
            indexes.append(i + 1)
        elif lines[i].startswith("> [!WARNING]"):
            admonition = True
            lines[i] = "!!! warning"
            indexes.append(i + 1)
        elif lines[i].startswith("> [!CAUTION]"):
            admonition = True
            lines[i] = '!!! failure "Caution"'
            indexes.append(i + 1)
        elif admonition and lines[i].startswith(">"):
            lines[i] = "\t" + lines[i][2:]
        elif admonition and not lines[i].startswith(">"):
            admonition = False

    for i in indexes:
        lines.insert(i, "")

    return "\n".join(lines)
