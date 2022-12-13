import aiohttp


class Http:
    async def request(self, url, data=None, method='POST'):
        for i in range(3):
            try:
                async with aiohttp.request(method,
                                           f'http://localhost:8000/{url}', json=data) as resp:
                    if resp.status != 200:
                        raise
                    return await resp.json()
            except:
                pass

    def startup_bot(self, name: str, symbols: list, user_data: dict, order_data: dict):
        return self.request('startup_bot',
                            data={'name': name, 'symbols': symbols, 'user_data': user_data, 'order_data': order_data})

    def disable_bot(self, name: str):
        return self.request('disable_bot', data={'name': name, })
