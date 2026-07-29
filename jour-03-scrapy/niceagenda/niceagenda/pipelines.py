from itemadapter import ItemAdapter


class CleanPipeline:
    """Nettoie les donnees texte."""

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        for field in ["titre", "date", "lieu"]:
            if a.get(field):
                a[field] = " ".join(a[field].split())
        return item