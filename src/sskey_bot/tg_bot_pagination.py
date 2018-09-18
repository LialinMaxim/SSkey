# test dada generator
user_passwords = [{'pass_id': i,
                   'title': f'title_{i}',
                   'login': f'login_{i}'} for i in range(1, 2)]


# print('--pass_list--', user_passwords)


def view_part(pass_list, page=0, elements=6):
    length = len(pass_list)
    if length % elements:
        pages = length // elements + 1
    else:
        pages = length // elements
    page = abs(pages + page) % pages

    start = page * elements
    if start == length:
        start = 0
    end = start + elements

    if end > length:
        passwords = pass_list[start:]
    else:
        passwords = pass_list[start:end]

    # print(f'page:{page}',f'length:{length}', f'start:{start}', f'end:{end}')

    view = ''
    for p in passwords:
        id = p.get('pass_id')
        title = p.get('title')
        login = p.get('login')
        view += f'/{id} - {title} : {login}\n'
    return view


# for tests
for i in range(-5, 5):
    print(f'<< page {i} >>')
    print(view_part(user_passwords, page=i))
