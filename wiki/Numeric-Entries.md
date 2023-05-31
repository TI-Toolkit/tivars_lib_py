### TIReal
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
            <td rowspan=3>Data</td>
            <td>Flags</td>
            <td>0</td>
            <td>1</td>
            <td><code>FloatFlags</code></td>
            <td>Flags for the real number</td>
            <td>
                <ul>
                    <li>If bit 1 is set, the number is undefined
                    <li>If bits 2 and 3 are set and bit 1 is clear, the number if half of a complex number
                    <li>If bit 6 is set, something happened
                    <li>If bit 7 is set, the number is negative
                </ul>
            </td>
        </tr>
        <tr>
            <td>Exponent</td>
            <td>1</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The exponent of the real number</td>
            <td>
                <ul>
                    <li>The exponent has a bias of 0x80
                </ul>
            </td>
        </tr>
        <tr>
            <td>Mantissa</td>
            <td>2</td>
            <td>7</td>
            <td><code>BCD</code></td>
            <td>The mantissa of the real number</td>
            <td>
                <ul>
                    <li>The mantissa is 14 digits stored in BCD format, two digits per byte
                </ul>
            </td>
        </tr>
    </tbody>
</table>

### TIComplex
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
            <td rowspan=8>Data</td>
            <td>Real Flags</td>
            <td>0</td>
            <td>1</td>
            <td><code>FloatFlags</code></td>
            <td>Flags for the real part of the complex number</td>
            <td>
                <ul>
                    <li>Bits 2 and 3 are set
                    <li>If bit 6 is set, something happened
                    <li>If bit 7 is set, the part is negative
                </ul>
            </td>
        </tr>
        <tr>
            <td>Real</td>
            <td>0</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The real part of the complex number</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Real Exponent</td>
            <td>1</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The exponent of the real part of the complex number</td>
            <td>
                <ul><li>The exponent has a bias of 0x80
                </ul>
            </td>
        </tr>
        <tr>
            <td>Real Mantissa</td>
            <td>2</td>
            <td>7</td>
            <td><code>BCD</code></td>
            <td>The mantissa of the real part of the complex number</td>
            <td>
                <ul><li>The mantissa is 14 digits stored in BCD format, two digits per byte
                </ul>
            </td>
        </tr>
        <tr>
            <td>Imag Flags</td>
            <td>9</td>
            <td>1</td>
            <td><code>FloatFlags</code></td>
            <td>Flags for the imaginary part of the complex number</td>
            <td>
                <ul>
                    <li>Bits 2 and 3 are set
                    <li>If bit 6 is set, something happened
                    <li>If bit 7 is set, the part is negative
                </ul>
            </td>
        </tr>
        <tr>
            <td>Imag</td>
            <td>9</td>
            <td>9</td>
            <td><code>TIReal</code></td>
            <td>The imaginary part of the complex number</td>
            <td>
                <ul>
                </ul>
            </td>
        </tr>
        <tr>
            <td>Imag Exponent</td>
            <td>10</td>
            <td>1</td>
            <td><code>Integer</code></td>
            <td>The exponent of the imaginary part of the complex number</td>
            <td>
                <ul>
                    <li>The exponent has a bias of 0x80
                </ul>
            </td>
        </tr>
        <tr>
            <td>Imag Mantissa</td>
            <td>11</td>
            <td>7</td>
            <td><code>BCD</code></td>
            <td>The mantissa of the imaginary part of the complex number</td>
            <td>
                <ul>
                    <li>The mantissa is 14 digits stored in BCD format, two digits per byte
                </ul>
            </td>
        </tr>
    </tbody>
</table>

