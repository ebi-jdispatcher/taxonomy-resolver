---
title: 'Taxonomy Resolver: A Python package for building and filtering taxonomy trees'
tags:
  - Python
  - Taxonomy
  - Tree
  - Hierarchy
  - NCBI Taxonomy
  - NCBI BLAST+
  - Nested Set Model
  - Modified Preorder Tree Traversal
authors:
  - name: Fábio Madeira
    orcid: 0000-0001-8728-9449
    corresponding: true
    affiliation: 1
  - name: Nandana Madhusoodanan
    orcid: 0000-0001-5004-152X
    affiliation: 1
  - name: Alberto Eusebi
    orcid: 0000-0001-5179-7724
    affiliation: 1
  - name: Joonheung Lee
    orcid: 0000-0002-5760-2761
    affiliation: 1
  - name: Ania Niewielska
    orcid: 0000-0003-0989-3389
    affiliation: 1
  - name: Sarah Butcher
    orcid: 0000-0002-4494-5124
    affiliation: 1
affiliations:
  - name: | 
      European Molecular Biology Laboratory, European Bioinformatics Institute (EMBL-EBI), 
      Wellcome Trust Genome Campus, Hinxton, Cambridge CB10 1SD, UK
    index: 1
date: 26 September 2024
bibliography: paper.bib

---

# Summary

Taxonomy classification provides an important source of information for studying biological systems. It is a key component for many areas of biological sciences research, particularly genetics, evolutionary biology, biodiversity and conservation [@sandall_globally_2023]. Common ancestry, homology and conservation of sequence and structure are all central ideas in biology that are directly related to the evolutionary history of any group of organisms [@ochoterena_search_2019]. The National Center for Biotechnology Information (NCBI) Taxonomy [@schoch_ncbi_2020] provides a curated classification and nomenclature for all the organisms in the public sequence databases, across the taxonomic ranks (i.e. Domain, Kingdom, Phylum, Class, Order, Family, Genus and Species). 

Here we describe ``Taxonomy Resolver``, a Python module and command-line interface (CLI) application for building and filtering taxonomy trees based on the NCBI Taxonomy. Taxonomy Resolver streamlines the process of manipulating trees, enabling fast tree traversal, searching and filtering.

# Statement of need

The NCBI Taxonomy Database [@schoch_ncbi_2020] provides a hierarchically arranged list of organisms across all domains of life found in the sequence databases. Tree filtering, i.e. generation of tree subsets, referred to as subtrees, has various applications for sequence analysis, particularly for reducing the search space of sequence similarity searching algorithms. A sequence dataset composed of sequences from diverse taxa can be more quickly searched if only a subset of sequences which belong to taxonomies of interest are selected. 

The NCBI BLAST+ suite is the most widely used toolset in bioinformatics for performing sequence similarity search [@camacho_blast_2009]. The suite provides a Bash script (`get_species_taxids.sh`) to convert NCBI Taxonomy identifiers (TaxIDs) or text into TaxIDs suitable for filtering sequence searches. While this is a useful utility, it only works with sequences submitted to GenBank or other NCBI-hosted databases, and more importantly, it relies on making API calls via Entrez Direct (EDirect) [@kans_entrez_2024]. EDirect requires an internet connection and it does not scale well when working with large sequence datasets. Other general-purpose tree libraries exist for Python (e.g. ``anytree`` [@anytree] and ``bigtree`` [@bigtree]) and R (e.g. ``ggtree`` [@yu_ggtree_2017]), but they do not support the core features provided by Taxonomy Resolver or focus mainly on tree visualisation. The development of Taxonomy Resolver started in 2020 and aims to provide user-friendly interfaces for working directly with the NCBI Taxonomy hierarchical dataset.

# Features

Taxonomy Resolver has been developed with simplicity in mind and it can be used both as a standard Python module or as a CLI application. The main tasks performed by Taxonomy Resolver are:

* **downloading** the NCBI Taxonomy classification hierarchy “dump” from the NCBI FTP server
* **building** complete taxonomy tree data structures or partial trees, i.e. subtrees
* **searching** particular TaxIDs at any level of the taxonomy hierarchy, performing fast tree traversal
* **validating** TaxIDs against the NCBI Taxonomy or any given subtree
* **generating** taxonomy lists that compose any subtree, at any level of the taxonomy hierarchy
* **filtering** a tree based on the inclusion and/or exclusion of certain TaxIDs
* **writing and loading** tree data structures using Python’s object serialisation

# Implementation

A taxonomy tree is a hierarchical structure that can be seen as a collection of deeply nested containers - nodes connected by edges, following the hierarchy, from the parent node - the root, all the way down to the children nodes - the leaves. An object-oriented programming (OOP) tree implementation based on recursion does not typically scale well for large trees, such as the NCBI Taxonomy, which is composed of >2.6 million nodes. To improve performance, Taxonomy Resolver represents the tree structure following the Nested Set Model, which is a technique developed to represent hierarchical data in relational databases lacking recursion capabilities. This allows for efficient and inexpensive querying of parent-child relationships. The full tree is traversed following the Modified Preorder Tree Traversal (MPTT) strategy [@celko_chapter_2004], in which each node in the tree is visited twice. In a preorder traversal, the root node is visited first, then recursively a preorder traversal of the left subtree, followed by a recursive preorder traversal of the right subtree, in order, until every node has been visited. The modified strategy allows capturing the 'left' and 'right' ($lft$ and $rgt$, respectively) boundaries of each subtree, which are stored as two additional attributes. Finding a subtree is as simple as searching for the nodes of interest where $lft > node's\ lft$ and $rgt < node's\ rgt$. Likewise, finding the full path to a node is as simple as searching for the nodes where $lft < node's\ lft$ and $rgt > node's\ rgt$. Traversal attributes, depth and node indexes are captured for each tree node and are stored as a pandas DataFrame [@pandas_2024].

Taxonomy Resolver has been developed to take advantage of the Nested Set Model tree structure, so it can perform fast validation and create lists of taxa that compose a particular subtree. Inclusion and exclusion lists can also be seamlessly used to produce subset trees with wide applications, particularly for sequence similarity search. Taxonomy Resolver has been in production since 2020 serving thousands of users every month. It provides taxonomy filtering features for NCBI BLAST+ provided by the popular EMBL-EBI Job Dispatcher service, available from [https://www.ebi.ac.uk/jdispatcher/sss/ncbiblast](https://www.ebi.ac.uk/jdispatcher/sss/ncbiblast) [@madeira_2024].

# Acknowledgements

We would like to thank current and past members of the EMBL-EBI for their continued support. We would like to also thank EMBL and its funders.

# References
