table_header = """<table>
    <thead>
        <tr>
            <th>Section</th>
            <th>Subsection</th>
            <th>Section Offset</th>
            <th>Length</th>
            <th>Type</th>
            <th>Description</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>"""

top_row = """
        <tr>
            <td rowspan={section.span}>{section.name}</td>
            <td>{subsection.name}</td>
            <td>{subsection.offset}</td>
            <td>{subsection.length}</td>
            <td><code>{subsection.type}</code></td>
            <td>{subsection.description}</td>
            <td>
                <ul>{subsection.notes}
                </ul>
            </td>
        </tr>"""

later_row = """
        <tr>
            <td>{subsection.name}</td>
            <td>{subsection.offset}</td>
            <td>{subsection.length}</td>
            <td><code>{subsection.type}</code></td>
            <td>{subsection.description}</td>
            <td>
                <ul>{subsection.notes}
                </ul>
            </td>
        </tr>"""

name_row = """
        <tr>
            <td><a href=Var-Files#TIEntry>Meta</a></td>
            <td>{subsection.name}</td>
            <td>{subsection.offset}</td>
            <td>{subsection.length}</td>
            <td><code>{subsection.type}</code></td>
            <td>{subsection.description}</td>
            <td>
                <ul>{subsection.notes}
                </ul>
            </td>
        </tr>
        <tr>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td>...</td>
        </tr>"""

table_footer = """
    </tbody>
</table>

"""
