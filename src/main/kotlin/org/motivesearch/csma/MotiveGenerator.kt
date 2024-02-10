package org.motivesearch.csma

data class MotiveUnit(val name: String)

data class MotivePosition(val position: Int, val length: Int)

data class Motive(val positions: List<MotivePosition>, val frequency: Int, val sequence: List<MotiveUnit>) {
    companion object {
        fun fromPositions(positions: List<MotivePosition>, sequence: List<MotiveUnit>) =
            Motive(positions, positions.size, sequence)
    }
}


class MotiveGenerator {

    fun generateMotives(
        sequence: List<MotiveUnit>,
        minFrequency: Int,
        maxGap: Int,
        minLength: Int,
        maxLength: Int
    ): List<Motive> {
        val basicMotives = getBasicMotives(sequence, minFrequency)

        var motivesOfIteration = basicMotives

        var motivesOfAllIterations = emptyList<Motive>()
        while (motivesOfIteration.isNotEmpty()) {
            motivesOfIteration =
                motiveOfIteration(motivesOfIteration, basicMotives, minFrequency, maxLength, maxGap)
            motivesOfAllIterations = motivesOfAllIterations + motivesOfIteration.filter { it.sequence.size >= minLength}
        }

        return motivesOfAllIterations
    }

    private fun motiveOfIteration(
        motivesOfLastIteration: List<Motive>,
        baseMotives: List<Motive>,
        minFrequency: Int,
        maxLength: Int,
        maxGap: Int
    ): List<Motive> {
        val motivesOfNextIteration = motivesOfLastIteration.map { motiveOfIteration ->
            val frequentPosition = getFrequentPosition(motiveOfIteration, minFrequency)
            val candidateExtensions = generateCandidateExtension(baseMotives, frequentPosition)

            candidateExtensions.map { candidateExtension ->
                mergeMotives(motiveOfIteration, candidateExtension, maxGap, maxLength)
            }
        }.flatten()

        return filterMotives(motivesOfNextIteration, minFrequency, maxLength)
    }

    fun getBasicMotives(sequence: List<MotiveUnit>, minFrequency: Int): List<Motive> {
        val basicMotiveUnits = sequence.toSet()

        val basicMotives =
            basicMotiveUnits.map { it to Motive(emptyList(), 0, listOf(it)) }
                .toMap().toMutableMap()

        sequence.forEachIndexed { index, motiveUnit ->
            val motive = basicMotives[motiveUnit]!!
            val newPositions = motive.positions.toMutableList()
            newPositions.add(MotivePosition(index, 1))
            basicMotives[motiveUnit] = motive.copy(positions = newPositions, frequency = motive.frequency + 1)
        }

        val basicMotivesAboveMinFrequency = basicMotives.filter { it.value.frequency >= minFrequency }

        return basicMotivesAboveMinFrequency.values.toList()
    }

    fun getMotiveUnits(sequence: String): List<MotiveUnit> {
        val uniqueValues = sequence.split(",")

        return uniqueValues.map { MotiveUnit(it) }
    }

    fun getFrequentPosition(motive: Motive, minFrequency: Int): Int {
        if (motive.frequency < minFrequency) throw IllegalArgumentException("Motiv frequency is less than minFrequency")

        val position = motive.positions[minFrequency - 1]
        return position.position + position.length
    }

    fun generateCandidateExtension(baseMotives: List<Motive>, frequentPosition: Int): List<Motive> {
        return baseMotives.filter { baseMotive ->
            baseMotive.positions.any { position -> position.position >= frequentPosition - 1 }
        }
    }

    fun mergeMotives(motive: Motive, candidateExtension: Motive, maxGap: Int, maxLength: Int): Motive {
        val newSequence = motive.sequence + candidateExtension.sequence

        val newPositions = motive.positions.map { position ->
            val nextCandidatePosition = candidateExtension.positions.filter { candidatePosition ->
                val notToLargeGap = candidatePosition.position - (position.position + position.length) <= maxGap
                val afterPosition = candidatePosition.position >= (position.position + position.length)
                val notToLong = candidatePosition.position + candidatePosition.length - position.position <= maxLength
                notToLargeGap && afterPosition && notToLong
            }.firstOrNull()

            if (nextCandidatePosition != null) {
                MotivePosition(position.position, position.length + nextCandidatePosition.length)
            } else {
                null
            }
        }.filterNotNull()

        return motive.copy(positions = newPositions, frequency = newPositions.size, sequence = newSequence)
    }

    private fun filterMotives(motives: List<Motive>, minFrequency: Int, maxLength: Int): List<Motive> {
        return motives.filter { it.frequency >= minFrequency && it.sequence.size <= maxLength }
    }


}