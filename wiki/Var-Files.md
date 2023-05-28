Every var file has two parts: a _header_ and a number of _entries_, where an entry contains the data for a single variable. Usually, var files contain just one entry; in these cases, there's not much distinction between a var and an entry for the purposes of messing with its data.

### TIHeader
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
            <td rowspan=4>Header</td>
            <td>Magic</td>
            <td>0</td>
            <td>8</td>
            <td><code>String</code></td>
            <td>The file magic for the var</td>
            <td>
                <ul>
                    <li>Used to identify if the file is intended for the TI-82 (<code>**TI82**</code>), TI-83 (<code>**TI83**</code>), or TI-83+ and onward (<code>**TI83F*</code>)
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extra</td>
            <td>8</td>
            <td>2</td>
            <td><code>Bytes</code></td>
            <td>Extra export bytes for the var</td>
            <td>
                <ul>
                    <li>Exact meaning and interpretation of these bytes is not yet determined
                </ul>
            </td>
        </tr>
        <tr>
            <td>Product ID</td>
            <td>10</td>
            <td>1</td>
            <td><code>Bytes</code></td>
            <td>The product ID for the var</td>
            <td>
                <ul>
                    <li>Used to identify the model the var was created on, though has no actual functional ramifications
                    <li>Does not constitute a 1-to-1 mapping to distinct models
                </ul>
            </td>
        </tr>
        <tr>
            <td>Comment</td>
            <td>11</td>
            <td>42</td>
            <td><code>String</code></td>
            <td>The comment attached to the var</td>
            <td></td>
        </tr>
    </tbody>
</table>

### TIEntry

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
            <td></td>
            <td>Meta Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the meta section of the entry</td>
            <td>
                <ul>
                    <li>Indicates if the entry is suitable for a flash chip (13) or not (11)
                    <li>If equal to 13, the entry contains the starred meta subsections
                    <li>If equal to 11, the entry lacks the starred meta subsections
                </ul>
            </td>
        </tr>
        <tr>
            <td rowspan=5>Meta</td>
            <td>Data Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the data section of the entry</td>
            <td></td>
        </tr>
        <tr>
            <td>Type ID</td>
            <td>2</td>
            <td>1</td>
            <td><code>Bytes</code></td>
            <td>The type ID of the entry</td>
            <td>
                <ul>
                    <li>Used the interpret the contents of the data section of the entry
                </ul>
            </td>
        </tr>
        <tr>
            <td>Name</td>
            <td>3</td>
            <td>8</td>
            <td>Varies</td>
            <td>The name of the entry</td>
            <td>
                <ul>
                    <li>Interpretation as text depends on the entry type; see entry pages for details
                </ul>
            </td>
        </tr>
        <tr>
            <td>Version*</td>
            <td>11</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The version number of the entry</td>
            <td>
                <ul>
                    <li>Only known use is for programs and other tokenized types
                </ul>
            </td>
        </tr>
        <tr>
            <td>Archived*</td>
            <td>12</td>
            <td>1</td>
            <td><code>Boolean</code></td>
            <td>Whether the entry is archived</td>
            <td></td>
        </tr>
        <tr>
            <td></td>
            <td>Data Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The length of the data section of the entry</td>
            <td>
                <ul>
                    <li>Repeat of the value found in the meta section
                </ul>
            </td>
        </tr>
        <tr>
            <td>Data</td>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td>The data section of the entry</td>
            <td>
                <ul>
                    <li>See entry pages for subsections
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIVar

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
            <td rowspan=2>Header</td>
            <td>Header</td>
            <td>0</td>
            <td>53</td>
            <td><code><a href="#TIHeader">TIHeader</a></code></td>
            <td>The var's header</td>
            <td></td>
        </tr>
        <tr>
            <td>Entry Length</td>
            <td>53</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The total length of all entries in the var</td>
            <td>
                <ul>
                    <li>Should be 57 less than the total var size
                </ul>
            </td>
        </tr>
        <tr>
            <td rowspan=2>Entries</td>
            <td>Entry 1</td>
            <td>0</td>
            <td>...</td>
            <td><code><a href="#TIEntry">TIEntry</a></code></td>
            <td>The first entry in the var</td>
            <td></td>
        </tr>
        <tr>
            <td>...</td>
            <td>...</td>
            <td>...</td>
            <td><code><a href="#TIEntry">TIEntry</a></code></td>
            <td>Subsequent entries in the var</td>
            <td>
                <ul>
                    <li>Most vars contain only one entry
                </ul>
            </td>
        </tr>
        <tr>
            <td>Checksum</td>
            <td>Checksum</td>
            <td>0</td>
            <td>2</td>
            <td><code>Bytes</code></td>
            <td>The checksum for the var</td>
            <td>
                <ul>
                    <li>Equal to the lower 2 bytes of the sum of all bytes in the entries
                </ul>
            </td>
        </tr>
    </tbody>
</table>