### TIRealList
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
            <td><code>ListName</code></td>
            <td>The name of the entry</td>
            <td>
                <ul>
                    <li>Must be 1 to 5 characters in length
                    <li>Can include any characters A-Z, 0-9, or θ
                    <li>Cannot start with a digit; use L1 - L6 instead
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
            <td>The length of the list</td>
            <td>
                <ul>
                    <li>Cannot exceed 999
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIComplexList
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
            <td><code>ListName</code></td>
            <td>The name of the entry</td>
            <td>
                <ul>
                    <li>Must be 1 to 5 characters in length
                    <li>Can include any characters A-Z, 0-9, or θ
                    <li>Cannot start with a digit; use L1 - L6 instead
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
            <td>The length of the list</td>
            <td>
                <ul>
                    <li>Cannot exceed 999
                </ul>
            </td>
        </tr>
    </tbody>
</table>

