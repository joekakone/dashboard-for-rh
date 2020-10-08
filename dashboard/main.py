import pandas as pd
import numpy as np
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.palettes import Category20c
from bokeh.models import DataTable, TableColumn, NumberFormatter, StringFormatter, ColumnDataSource

# Loading data
rh = pd.read_csv('dashboard/HRDataset_v13.csv')


##### KPIS #####
# Number of employees
nb_employees = len(rh)

# Salary mean and total
salary_mean = round(rh.PayRate.mean(), 2)
salary_total = round(rh.PayRate.sum(), 2)

# Number of departments
nb_departments = rh.Department.nunique()

##### Charts #####

# Sex Pie Chart 
sex = rh.Sex.value_counts().reset_index(name='count')
sex = sex.rename(columns={'index': 'sex'})

sex_tooltips = '@sex: @count (@percent)'

sex['percent'] = sex['count']/sex['count'].sum() * 100
sex['percent']  = sex['percent'].apply(lambda x: str(round(x, 2))+'%')
sex['angle'] = sex['count']/sex['count'].sum() * 2*3.14
sex['color'] = ['pink', 'gray']

p_sex = figure(x_range=(-0.6, 1), plot_width=300, plot_height=200,
           title='', toolbar_location=None, name='p_sex',
           tools='hover', tooltips=sex_tooltips)

p_sex.annular_wedge(x=0, y=1, inner_radius=0.35, outer_radius=0.5,
                    start_angle=cumsum('angle', include_zero=True),
                    end_angle=cumsum('angle'), line_color='white',
                    fill_color='color', legend_field='sex', source=sex)

p_sex.axis.axis_label=None
p_sex.axis.visible=False
p_sex.grid.grid_line_color = None

curdoc().add_root(p_sex)

# Department BarhPlot
departments = rh.Department.value_counts().reset_index(name='count')
departments = departments.rename(columns={'index': 'department'})

# departments['color'] = Category20c[len(departments)]
dep_tooltips = '@department: @count'

p_departments = figure(y_range=list(reversed(departments.department)),
                  plot_width=600, height=200, name='p_departments',
                  toolbar_location=None, tools='hover', tooltips=dep_tooltips)

p_departments.hbar(y='department', right='count', color='gray', source=departments, height=0.7)

p_departments.x_range.start = 0
p_departments.ygrid.grid_line_color = None

curdoc().add_root(p_departments)

### Table for departments size ###
departments = ColumnDataSource(departments)
columns = [
    TableColumn(field="department", title="Department"),
    TableColumn(field="count", title="Size",
                formatter=StringFormatter(text_align="center")),
]
department_table = DataTable(source=departments, columns=columns, height=300, width=300, name="department_table")

curdoc().add_root(department_table)

#### BarPlot for Hire and Terminaison ####
def f(x):
    if x in [np.NaN, ['nan']]:
        y = np.NaN
    else:
        date = str(x).split('/')
        y = date[2]
        if len(y) == 2:
            y = '20' + date[2]
    return y

hires = rh.DateofHire.apply(f)
hires = hires.value_counts()
hires = hires.sort_index()
hires = hires.reset_index(name='hire').rename(columns={'index': 'year'})

terminaisons = rh.DateofTermination.apply(f)
terminaisons = terminaisons.value_counts() * (-1)
terminaisons = terminaisons.sort_index()
terminaisons = terminaisons.reset_index(name='terminaison').rename(columns={'index': 'year'})

mvts = pd.merge(hires, terminaisons)
mvts['diff'] = mvts.hire + mvts.terminaison

p_mvts_tooltips="@year: @diff"

p_mvts = figure(x_range=mvts.year,
                  plot_width=900, height=300, name='p_mvts',
                  toolbar_location=None, tools="", tooltips=p_mvts_tooltips)

p_mvts.vbar(x="year", top="hire", width=0.5, color='pink', legend_label='Hire', source=mvts)

p_mvts.vbar(x="year", top="terminaison", width=0.5, color='gray', legend_label='Terminaison', source=mvts)

p_mvts.line(x="year", y="diff", color='blue', legend_label='Diff', source=mvts)

p_mvts.circle(x="year", y="diff", color='black', source=mvts)

curdoc().add_root(p_mvts)


#### Histogram for Top Salaries
salaries = rh.PayRate.dropna()

p_salaries = figure(plot_width=300, plot_height=300,
                    name='p_salaries', toolbar_location=None,
                    tools="", tooltips=None)
hist, edges = np.histogram(salaries, bins=30)

p_salaries.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], color='gray')
p_salaries.y_range.start = 0

curdoc().add_root(p_salaries)


curdoc().title = 'RH Dashboard'
curdoc().template_variables['kpi_names'] = ['nb_employees', 'salary_total', 'salary_mean', 'nb_departments']
curdoc().template_variables['kpis'] = {
    'nb_employees': {
        'title': 'Number of employees',
        'value': nb_employees
        },
    'salary_total': {
        'title': 'Total salary',
        'value': '$ ' + str(salary_total)
        },
    'salary_mean': {
        'title': 'Mean salary',
        'value': '$ ' + str(salary_mean)
        },
    'nb_departments': {
        'title': 'Total departments', 
        'value': nb_departments
        },
}