import sys
import originpro as op
import os
import pandas as pd


def origin_shutdown_exception_hook(exctype, value, traceback):
    op.exit()
    sys.__excepthook__(exctype, value, traceback)


class OriginLabGraphing:
    def __init__(self, data_path, result_path, search_file="result") -> None:
        self.result_path = result_path
        self.data_path = data_path
        self.search_file_name = search_file
        self.data_file_path_list, self.data_file_name_list = self.search_file(
            self.data_path, self.search_file_name)

    def search_file(self, dir_path, search_file_name):
        data_file_path_list = []
        data_file_name_list = []
        for (path, dir, files) in os.walk(dir_path):
            for filename in files:
                ext = os.path.splitext(filename)[0]
                if search_file_name in ext:
                    data_file_path_list.append(os.path.join(path, filename))
                    data_file_name_list.append(ext)

        return data_file_path_list, data_file_name_list

    def draw(self, file_path, scale, name):
        df = pd.read_csv(file_path)

        # Create a new book with sheet and add generated data.
        wks = op.new_sheet(lname=name)
        wks.from_list(0, df["X"], lname='X', axis='X')
        wks.from_list(1, df["mean"], lname='mean', axis='Y')
        wks.from_list(2, df["std"], lname='std', axis='E')

        self.draw_graph(wks, scale, name)

    def draw_graph(self, wks, scale, name):
        # 3. Create a graph
        graph = op.new_graph(f"{name}_{scale}")
        gl = graph[0]
        plot = gl.add_plot(wks, coly=1, colx=0, type='line', colyerr=2)

        # Customize Plot
        plot.color = '#000000'
        plot.set_cmd('-w 1000')

        # Customize Graph
        gl.set_xlim(scale[0], scale[1])
        gl.group()
        gl.rescale('x')
        gl.axis('x').title = 'Wavenumber (cm-1)'
        gl.axis('y').title = 'Transmittance'
        gl.set_int('showframe', 1)

        # Customize Legend
        lgnd = gl.label('Legend')
        lgnd.remove()

    def graphing(self, scale=[800, 2000]):
        if op and op.oext:
            sys.excepthook = origin_shutdown_exception_hook

        # Set Origin instance visibility.
        # Important for only external Python.
        # Should not be used with embedded Python.
        if op.oext:
            op.set_show(True)

        # 6. Draw all the files imported in the same way as a graph
        for i, file_name in enumerate(self.data_file_name_list):
            file_path = self.data_file_path_list[i]

            self.draw(file_path, scale, file_name)

        op.save(os.path.join(self.result_path,
                f"{self.data_file_name_list[0]}~{self.data_file_name_list[-1]}.opju"))

        # Exit running instance of Origin.
        # Required for external Python but don't use with embedded Python.
        if op.oext:
            op.exit()


if __name__ == '__main__':
    og = OriginLabGraphing(data_path=r'C:\Users\wlans\Documents\GitHub\opus\opus\result',
                           result_path=r'C:\Users\wlans\Documents\GitHub\opus\opus\origin_result')
    og.graphing()
