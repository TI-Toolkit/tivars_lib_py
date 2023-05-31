### TIMonoPicture
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

### TIPicture
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

### TIImage
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
        <tr>
            <td>Image Magic</td>
            <td>2</td>
            <td>1</td>
            <td><code>Bytes</code></td>
            <td>Magic to identify the var as an image</td>
            <td>
                <ul>
                    <li>Always set to 0x81
                </ul>
            </td>
        </tr>
    </tbody>
</table>

