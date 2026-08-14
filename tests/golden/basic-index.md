# Basic Project {#basic-project}

Prose with Vue hazards: a generic type like `List<T>` in code, raw
angle text 1 &lt; 2 &gt; 0, and a template placeholder &#123;&#123; mustache }} in plain text.
Inline code with a mustache: <span v-pre>`{{ name }}`</span>.

<a id="custom-label"></a>

## Section One {#section-one}

::: tip Note
Notes become VitePress tip containers.
:::

::: warning Warning
Warnings stay warnings.
:::

::: danger Danger
Danger becomes a danger container.
:::

::: info Custom Box
Generic admonitions keep their custom title.
:::

::: info See also
Cross-reference [Section One](#custom-label) and the [Other Page](other.md) page.
:::

## Code {#code}

```python
def f(x):
    return {"a": x < 2}
```

A doctest block:

```python
>>> 1 + 1
2
```

## Math {#math}

Inline $E = h\nu$ and a block:

$$
B_\nu(T) = \frac{2 h \nu^3}{c^2} \frac{1}{e^{h\nu/k_B T} - 1}
$$

## Lists and Tables {#lists-and-tables}

* item one
* item two
  * nested item

| Name   |   Value |
|--------|---------|
| alpha  |       1 |
| beta   |       2 |
