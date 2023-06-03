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
            <td rowspan=19>Data</td>
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
            <td>Mode Id</td>
            <td>3</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The mode ID for the GDB</td>
            <td>
                <ul>
                    <li>Always 0x20
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
            <td>The leftmost graphscreen coordinate</td>
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
            <td>The rightmost graphscreen coordinate</td>
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
            <td>The bottommost graphscreen coordinate</td>
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
            <td>The topmost graphscreen coordinate</td>
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
            <td>94</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The 1st equation in polar mode</td>
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
            <td>The 2nd equation in polar mode</td>
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
            <td>The 3rd equation in polar mode</td>
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
            <td>The 4th equation in polar mode</td>
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
            <td>The 5th equation in polar mode</td>
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
            <td>The 6th equation in polar mode</td>
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
            <td rowspan=25>Data</td>
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
            <td>Mode Id</td>
            <td>3</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The mode ID for the GDB</td>
            <td>
                <ul>
                    <li>Always 0x20
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
            <td>The leftmost graphscreen coordinate</td>
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
            <td>The rightmost graphscreen coordinate</td>
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
            <td>The bottommost graphscreen coordinate</td>
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
            <td>The topmost graphscreen coordinate</td>
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
            <td>94</td>
            <td>...</td>
            <td><code>TIGraphedEquation</code></td>
            <td>The 1st equation in polar mode</td>
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
            <td>The 2nd equation in polar mode</td>
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
            <td>The 3rd equation in polar mode</td>
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
            <td>The 4th equation in polar mode</td>
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
            <td>The 5th equation in polar mode</td>
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
            <td>The 6th equation in polar mode</td>
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
            <td><code>GlobalLineStyle</code></td>
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

