import sys
import originpro as op
import os
import pandas as pd


def origin_shutdown_exception_hook(exctype, value, traceback):
    op.exit()
    sys.__excepthook__(exctype, value, traceback)


class OriginLabGraphing:
    def __init__(self, result_path, data_path) -> None:
        self.result_path = result_path
        self.data_path = data_path
        self.data_dir = os.listdir(self.data_path)

    def draw(self, file_path, scale, name):
        df = pd.read_csv(file_path)

        # Create a new book with sheet and add generated data.
        wks = op.new_sheet(lname=name)
        wks.from_list(0, df["Unnamed: 0"], lname='X', axis='X')
        wks.from_list(1, df["mean"], lname='mean', axis='Y')
        wks.from_list(2, df["std"], lname='std', axis='E')

        for i in scale:
            self.draw_graph(wks, i, name)

    def draw_graph(self, wks, scale, name):
        # 3. Create a graph
        graph = op.new_graph(f"{name}_{scale}")
        gl = graph[0]
        plot = gl.add_plot(wks, coly=1, colx=0, type='line', colyerr=2)
        gl.set_xlim(scale, 800)
        gl.group()
        gl.rescale('x')
        gl.axis('x').title = 'Wavenumber (cm-1)'
        gl.axis('y').title = 'Transmittance'

        # Customize Legend
        lgnd = gl.label('Legend')
        lgnd.remove()

    def graphing(self):
        if op and op.oext:
            sys.excepthook = origin_shutdown_exception_hook

        # Set Origin instance visibility.
        # Important for only external Python.
        # Should not be used with embedded Python.
        if op.oext:
            op.set_show(True)

        data_files = [f for f in os.listdir(
            self.data_path) if f.endswith('.csv')]

        # 6. Draw all the files imported in the same way as a graph
        for file in data_files:
            file_name = file.split('.')[0]
            file_path = os.path.join(self.data_path, file)

            self.draw(file_path, [4000, 2000], file_name)

        op.save(os.path.join(self.result_path, f"{file_name}.opju"))

        # Exit running instance of Origin.
        # Required for external Python but don't use with embedded Python.
        if op.oext:
            op.exit()


if __name__ == '__main__':
    og = OriginLabGraphing(data_path=r'C:\Users\wlans\Documents\GitHub\opus\opus\result',
                           result_path=r'C:\Users\wlans\Documents\GitHub\opus\opus\origin_result')
    og.graphing()
