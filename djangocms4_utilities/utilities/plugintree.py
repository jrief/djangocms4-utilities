from cms.models.placeholdermodel import Placeholder


def check_tree(placeholder, language=None):
    """checks the plugin tree if the placeholder for common inconsistencies and returns a list
    of messages describing the inconsistency. Returns list of messages."""
    messages = []

    if language is None:
        languages = (
            placeholder.cmsplugin_set.order_by("language")
            .values_list("language", flat=True)
            .distinct()
        )
        for language in languages:
            message = check_tree(placeholder, language)
            if message is not None:
                messages += message
        return messages

    # Check 1: Positions are consecutive starting at 1
    position_list = list(placeholder.cmsplugin_set.values_list("position", flat=True))
    if position_list != list(
        range(1, placeholder.get_last_plugin_position(language) + 1)
    ):
        messages.append(
            f"{language}: Non consecutive position entries: {position_list}"
        )

    # Check 2: Children AFTER parents
    parent_list = list(placeholder.cmsplugin_set.values_list("parent", flat=True))
    for parent in parent_list:
        if parent is not None:
            parent_position = placeholder.cmsplugin_set.filter(pk=parent).first()
            if parent_position is not None:
                children_positions = placeholder.cmsplugin_set.filter(
                    parent=parent
                ).values_list("position", flat=True)
                print(children_positions, len(children_positions))
                if children_positions:
                    if min(children_positions) <= parent_position.position:
                        messages.append(
                            f"{language}: Children with positions lower than their parent's (id={parent}) position"
                        )
                    elif max(children_positions) - min(children_positions) + 1 > len(
                        children_positions
                    ):
                        messages.append(
                            f"{language}: Gap in children positions of parent (id={parent})"
                        )
    # Check 3: parents belonging to other placeholders
    for plugin in placeholder.cmsplugin_set.all():
        if plugin.parent and plugin.parent.placeholder != placeholder:
            messages.append(
                f"{language}: Plugins claim to be children of parents in a different placeholder"
            )

    return messages


def fix_tree(placeholder, language=None):
    """rebuilds the plugin tree for the placeholder. The resulting tree will look like this:
    Parent 1, position 1
        Child 1, position 2
        Parent 2, position 3
            Child 2, position 4
        Child 3, position 5
    Parent 3, position 6
        Child 4 position 7
    Child 5, position 8   # (Parent link to parent plugin in other placeholder removed)
    """
    if language is None:
        languages = (
            placeholder.cmsplugin_set.order_by("language")
            .values_list("language", flat=True)
            .distinct()
        )
        for language in languages:
            fix_tree(placeholder, language)
        return

    # First cut links to other placeholders
    for plugin in placeholder.cmsplugin_set.filter(language=language):
        if plugin.parent and plugin.parent.placeholder != placeholder:
            plugin.update(
                parent=None
            )  # At this point the tree is seriously broken: Cut the link

    # Then rebuild tree
    def build_tree(self, parent):
        nonlocal position

        for plugin in self.cmsplugin_set.filter(
            parent=parent, language=language
        ).order_by("position"):
            position += 1
            plugin.update(position=position)
            build_tree(self, plugin)

    position = placeholder.get_last_plugin_position(language)
    build_tree(placeholder, None)

    placeholder._recalculate_plugin_positions(language)


def get_draft_placeholders():
    if "djangocms_versioning" in settings.INSTALLED_APPS:

        unassigned = Placeholder.objects.filter(content_type=None)
        from django.contrib.contenttypes.models import ContentType

        ContentType.objects.filter()

        return unassigned
    else:
        return Placeholder.objects.all()