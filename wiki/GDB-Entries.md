### TIGraphedEquation
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
            <td rowspan=1>Flags</td>
            <td>Flags</td>
            <td>0</td>
            <td>1</td>
            <td><code>EquationFlags</code></td>
            <td>The flags for the equation</td>
            <td>
                <ul>
                    <li>Whether the equation is selected, used for graphing, or is participating in a link transfer
                </ul>
            </td>
        </tr>
        <tr>
            <td rowspan=1>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>The total size of the tokens</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIMonoGDB
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
            <td rowspan=9>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIGDB
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
            <td rowspan=14>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Grid Color</td>
            <td>-5</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the grid</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Axes Color</td>
            <td>-4</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the axes</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Global Style</td>
            <td>-3</td>
            <td>1</td>
            <td><code>GlobalStyle</code></td>
            <td>The line style for all plotted equations</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Border Color</td>
            <td>-2</td>
            <td>1</td>
            <td><code>BorderColor</code></td>
            <td>The color of the graph border</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Mode Flags</td>
            <td>-1</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for extended color mode settings</td>
            <td>
                <ul>
                    <li>Only DetectAsymptotesOn/Off is stored here
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIMonoFuncGDB
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
            <td rowspan=20>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xres</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The pixel separation of points in a function plot</td>
            <td>
                <ul>
                    <li>Must be an integer between 1 and 8
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y1</td>
            <td>70</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y2</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y3</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y4</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y5</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y6</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y7</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The seventh equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y8</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The eight equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y9</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The ninth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y0</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The tenth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIFuncGDB
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
            <td rowspan=26>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xres</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The pixel separation of points in a function plot</td>
            <td>
                <ul>
                    <li>Must be an integer between 1 and 8
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y1</td>
            <td>70</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y2</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y3</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y4</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y5</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y6</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y7</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The seventh equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y8</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The eight equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y9</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The ninth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y0</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The tenth equation in function mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Magic</td>
            <td>-18</td>
            <td>3</td>
            <td><code>String</code></td>
            <td>Magic to identify the GDB as color-oriented</td>
            <td>
                <ul>
                    <li>Always set to 84C
                </ul>
            </td>
        </tr>
        <tr>
            <td>Grid Color</td>
            <td>-5</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the grid</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Axes Color</td>
            <td>-4</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the axes</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Global Style</td>
            <td>-3</td>
            <td>1</td>
            <td><code>GlobalStyle</code></td>
            <td>The line style for all plotted equations</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Border Color</td>
            <td>-2</td>
            <td>1</td>
            <td><code>BorderColor</code></td>
            <td>The color of the graph border</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Mode Flags</td>
            <td>-1</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for extended color mode settings</td>
            <td>
                <ul>
                    <li>Only DetectAsymptotesOn/Off is stored here
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIMonoParamGDB
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
            <td rowspan=24>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmin</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial time</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmax</td>
            <td>70</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The final time</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tstep</td>
            <td>79</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The time increment</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X1T</td>
            <td>88</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y1T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X2T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y2T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X3T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y3T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X4T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y4T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X5T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y5T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X6T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y6T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIParamGDB
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
            <td rowspan=30>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmin</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial time</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmax</td>
            <td>70</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The final time</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tstep</td>
            <td>79</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The time increment</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X1T</td>
            <td>88</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y1T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X2T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y2T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X3T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y3T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X4T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y4T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X5T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y5T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>X6T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth X-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Y6T</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth Y-component in parametric mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Magic</td>
            <td>-14</td>
            <td>3</td>
            <td><code>String</code></td>
            <td>Magic to identify the GDB as color-oriented</td>
            <td>
                <ul>
                    <li>Always set to 84C
                </ul>
            </td>
        </tr>
        <tr>
            <td>Grid Color</td>
            <td>-5</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the grid</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Axes Color</td>
            <td>-4</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the axes</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Global Style</td>
            <td>-3</td>
            <td>1</td>
            <td><code>GlobalStyle</code></td>
            <td>The line style for all plotted equations</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Border Color</td>
            <td>-2</td>
            <td>1</td>
            <td><code>BorderColor</code></td>
            <td>The color of the graph border</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Mode Flags</td>
            <td>-1</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for extended color mode settings</td>
            <td>
                <ul>
                    <li>Only DetectAsymptotesOn/Off is stored here
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIMonoPolarGDB
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
            <td rowspan=18>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>θmin</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial angle</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>θmax</td>
            <td>70</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The final angle</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>θstep</td>
            <td>79</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The angle increment</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r1</td>
            <td>88</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r1</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r3</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r4</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r5</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r6</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIPolarGDB
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
            <td rowspan=24>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>θmin</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial angle</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>θmax</td>
            <td>70</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The final angle</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>θstep</td>
            <td>79</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The angle increment</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r1</td>
            <td>88</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r1</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r3</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r4</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fourth equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r5</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The fifth equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>r6</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The sixth equation in polar mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Magic</td>
            <td>-14</td>
            <td>3</td>
            <td><code>String</code></td>
            <td>Magic to identify the GDB as color-oriented</td>
            <td>
                <ul>
                    <li>Always set to 84C
                </ul>
            </td>
        </tr>
        <tr>
            <td>Grid Color</td>
            <td>-5</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the grid</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Axes Color</td>
            <td>-4</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the axes</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Global Style</td>
            <td>-3</td>
            <td>1</td>
            <td><code>GlobalStyle</code></td>
            <td>The line style for all plotted equations</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Border Color</td>
            <td>-2</td>
            <td>1</td>
            <td><code>BorderColor</code></td>
            <td>The color of the graph border</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Mode Flags</td>
            <td>-1</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for extended color mode settings</td>
            <td>
                <ul>
                    <li>Only DetectAsymptotesOn/Off is stored here
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIMonoSeqGDB
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
            <td rowspan=23>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Sequence Flags</td>
            <td>5</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the sequence mode settings</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStart</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of n for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMax</td>
            <td>70</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The final value of n</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>u(nMin)</td>
            <td>79</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of u at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin)</td>
            <td>88</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of v at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMin</td>
            <td>97</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of n for sequential equations</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>u(nMin + 1)</td>
            <td>106</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of u at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin + 1)</td>
            <td>115</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of v at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin)</td>
            <td>124</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of w at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStep</td>
            <td>133</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The n increment for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin + 1)</td>
            <td>142</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of w at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>u</td>
            <td>151</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first equation in sequence mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second equation in sequence mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>w</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third equation in sequence mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TISeqGDB
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
            <td rowspan=29>Data</td>
            <td>Length</td>
            <td>0</td>
            <td>2</td>
            <td><code>Integer</code></td>
            <td>Two less than the length of the GDB</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mode Flags</td>
            <td>4</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the mode settings</td>
            <td>
                <ul>
                    <li>Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
                </ul>
            </td>
        </tr>
        <tr>
            <td>Sequence Flags</td>
            <td>5</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the sequence mode settings</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Extended Mode Flags</td>
            <td>6</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for the extended mode settings</td>
            <td>
                <ul>
                    <li>ExprOn/Off and sequence plot offsets for sequence mode
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmin</td>
            <td>7</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>16</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>25</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>34</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>43</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>52</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStart</td>
            <td>61</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of n for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMax</td>
            <td>70</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The final value of n</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>u(nMin)</td>
            <td>79</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of u at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin)</td>
            <td>88</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of v at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMin</td>
            <td>97</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of n for sequential equations</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>u(nMin + 1)</td>
            <td>106</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of u at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin + 1)</td>
            <td>115</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of v at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin)</td>
            <td>124</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of w at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStep</td>
            <td>133</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The n increment for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin + 1)</td>
            <td>142</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The initial value of w at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>u</td>
            <td>151</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The first equation in sequence mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The second equation in sequence mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>w</td>
            <td>...</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The third equation in sequence mode</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Magic</td>
            <td>-11</td>
            <td>3</td>
            <td><code>String</code></td>
            <td>Magic to identify the GDB as color-oriented</td>
            <td>
                <ul>
                    <li>Always set to 84C
                </ul>
            </td>
        </tr>
        <tr>
            <td>Grid Color</td>
            <td>-5</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the grid</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Axes Color</td>
            <td>-4</td>
            <td>1</td>
            <td><code>GraphColor</code></td>
            <td>The color of the axes</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Global Style</td>
            <td>-3</td>
            <td>1</td>
            <td><code>GlobalStyle</code></td>
            <td>The line style for all plotted equations</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Border Color</td>
            <td>-2</td>
            <td>1</td>
            <td><code>BorderColor</code></td>
            <td>The color of the graph border</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Color Mode Flags</td>
            <td>-1</td>
            <td>1</td>
            <td><code>GraphMode</code></td>
            <td>The flags for extended color mode settings</td>
            <td>
                <ul>
                    <li>Only DetectAsymptotesOn/Off is stored here
                </ul>
            </td>
        </tr>
    </tbody>
</table>

