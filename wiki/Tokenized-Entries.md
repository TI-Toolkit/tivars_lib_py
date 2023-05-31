### TIEquation
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
            <td rowspan=1>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the data section following this entry</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIString
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
            <td rowspan=1>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the data section following this entry</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIProgram
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
            <td><a href=Var-Files#TIEntry>Meta</a></td>
            <td>Name</td>
            <td>0</td>
            <td>8</td>
            <td><code>String</code></td>
            <td>The name of the entry</td>
            <td>
                <ul>
                    <li>Must be 1 to 8 characters in length
                    <li>Can include any characters A-Z, 0-9, or Θ
                    <li>Cannot start with a digit
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
        </tr>
        <tr>
            <td rowspan=1>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the data section following this entry</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIProtectedProgram
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
            <td><a href=Var-Files#TIEntry>Meta</a></td>
            <td>Name</td>
            <td>0</td>
            <td>8</td>
            <td><code>String</code></td>
            <td>The name of the entry</td>
            <td>
                <ul>
                    <li>Must be 1 to 8 characters in length
                    <li>Can include any characters A-Z, 0-9, or Θ
                    <li>Cannot start with a digit
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
        </tr>
        <tr>
            <td rowspan=1>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the data section following this entry</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>
