package org.example.org.motivesearch

import org.motivesearch.csma.MotiveGenerator

fun main() {
    val motiveUnits = MotiveGenerator().getMotiveUnits("A,B,A,B,C,D,C,A,B,D,C,E")

    val finalMotives = MotiveGenerator().generateMotives(motiveUnits, 2, 1, 1, 4)

    finalMotives.forEach(::println)
}