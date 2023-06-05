### TIWindowSettings
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
                    <li>Always equal to Window
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
            <td rowspan=23>Data</td>
            <td>Xmin</td>
            <td>3</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>12</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>21</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>30</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>39</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>48</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Θmin</td>
            <td>57</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial angle for polar plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Θmax</td>
            <td>66</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the final angle for polar plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Θstep</td>
            <td>75</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the angle increment for polar plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmin</td>
            <td>84</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial time for parametric plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmax</td>
            <td>93</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the final time for parametric plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tstep</td>
            <td>102</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the time increment for parametric plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStart</td>
            <td>111</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of n for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMax</td>
            <td>120</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the final value of n for sequential equations and plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>u(nMin)</td>
            <td>129</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of u at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin)</td>
            <td>138</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of v at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMin</td>
            <td>147</td>
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
            <td>156</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of u at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin + 1)</td>
            <td>165</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of v at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin)</td>
            <td>174</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of w at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStep</td>
            <td>183</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the n increment for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xres</td>
            <td>192</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the pixel separation of points in a function plot</td>
            <td>
                <ul>
                    <li>Must be an integer between 1 and 8
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin + 1)</td>
            <td>201</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of w at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIRecallWindow
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
                    <li>Always equal to RclWindw
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
            <td rowspan=23>Data</td>
            <td>Xmin</td>
            <td>2</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the smallest or leftmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xmax</td>
            <td>11</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the largest or rightmost horizontal coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xscl</td>
            <td>20</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the separation between ticks on the horizontal axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymin</td>
            <td>29</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the smallest or bottommost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Ymax</td>
            <td>38</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the largest or topmost vertical coordinate on the graphscreen</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Yscl</td>
            <td>47</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the separation between ticks on the vertical axis</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Θmin</td>
            <td>56</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial angle for polar plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Θmax</td>
            <td>65</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the final angle for polar plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Θstep</td>
            <td>74</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the angle increment for polar plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmin</td>
            <td>83</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial time for parametric plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tmax</td>
            <td>92</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the final time for parametric plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Tstep</td>
            <td>101</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the time increment for parametric plots</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStart</td>
            <td>110</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of n for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMax</td>
            <td>119</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the final value of n for sequential equations and plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>u(nMin)</td>
            <td>128</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of u at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin)</td>
            <td>137</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of v at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>nMin</td>
            <td>146</td>
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
            <td>155</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of u at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>v(nMin + 1)</td>
            <td>164</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of v at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin)</td>
            <td>173</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of w at nMin</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>PlotStep</td>
            <td>182</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the n increment for sequential plots</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>Xres</td>
            <td>191</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the pixel separation of points in a function plot</td>
            <td>
                <ul>
                    <li>Must be an integer between 1 and 8
                </ul>
            </td>
        </tr>
        <tr>
            <td>w(nMin + 1)</td>
            <td>200</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value of w at nMin + 1</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TITableSettings
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
                    <li>Always equal to TblSet
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
            <td rowspan=2>Data</td>
            <td>TblMin</td>
            <td>2</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the initial value for the table</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
        <tr>
            <td>ΔTbl</td>
            <td>11</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>the increment for the table</td>
            <td>
                <ul>
                    <li>Must be an integer
                </ul>
            </td>
        </tr>
    </tbody>
</table>

