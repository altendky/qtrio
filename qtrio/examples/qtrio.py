async def together(a_signal):
        with open(self.some_path, 'w') as file:
            async with qtrio.enter_emissions_channel(signals=[a_signal]) as emissions:
                file.write('before')
                emission = await emissions.channel.receive()
                [value] = emission.args
                file.write(f'after {value!r}') 
