class Pagination():
    @staticmethod
    def get_page(some_list, page=1, step=10):
        page -= 1
        length = len(some_list)
        if length % step:
            pages = length // step + 1
        else:
            pages = length // step
        page = abs(pages + page) % pages
        start = page * step
        if start == length:
            start = 0
        end = start + step
        if end > length:
            return {'data_list': some_list[start:], 'page': page + 1, 'pages': pages, 'length': length}
        else:
            return {'data_list': some_list[start:end], 'page': page + 1, 'pages': pages, 'length': length}
