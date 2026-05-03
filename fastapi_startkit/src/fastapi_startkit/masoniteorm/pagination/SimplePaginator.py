from .BasePaginator import BasePaginator


class SimplePaginator(BasePaginator):
    def __init__(self, result, per_page, current_page, url=None):
        self.current_page = current_page
        self.per_page = per_page
        # Detect next page from the extra record fetched by the builder
        has_more = len(result) > per_page
        self.next_page = (int(self.current_page) + 1) if has_more else None
        self.previous_page = (int(self.current_page) - 1) or None
        self.url = url
        # Trim to per_page after detecting more pages
        self.result = result[:per_page]
        self.count = len(self.result)

    def serialize(self, *args, **kwargs):
        return {
            "data": self.result.serialize(*args, **kwargs),
            "meta": {
                "next_page": self.next_page,
                "count": self.count,
                "previous_page": self.previous_page,
                "current_page": self.current_page,
            },
        }

    def has_more_pages(self):
        return self.next_page is not None
