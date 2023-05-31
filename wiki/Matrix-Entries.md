### TIMatrix
<table>
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
    <tbody>
        <tr>
            <td rowspan=2>Data</td>
            <td>Width</td>
            <td>0</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The number of columns in the matrix</td>
            <td>
                <ul>
                    <li>Cannot exceed 255, though TI-OS imposes a limit of 99
                </ul>
            </td>
        </tr>
        <tr>
            <td>Height</td>
            <td>1</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The number of rows in the matrix</td>
            <td>
                <ul>
                    <li>Cannot exceed 255, though TI-OS imposes a limit of 99
                </ul>
            </td>
        </tr>
    </tbody>
</table>

