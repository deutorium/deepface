import tensorflow as tf


class DataEngineTypical:
	def path_yielder(self):
		for path in tf.io.gfile.listdir(self.main_path):
			splitted = path.split("_")
			try:
				age, sex, eth, _ = splitted

				yield self.main_path+path, (str(int(int(age)/5)), sex, eth)
			except ValueError:
				continue

	def path_yielder_age(self):
		for path in tf.io.gfile.listdir(self.main_path):
			splitted = path.split("_")
			try:
				age, _, _, _ = splitted

				yield self.main_path+path, int(int(age)/5)
			except ValueError:
				continue

	def path_yielder_sex(self):
		for path in tf.io.gfile.listdir(self.main_path):
			splitted = path.split("_")
			try:
				_, sex, _, _ = splitted

				yield self.main_path+path, int(sex)
			except ValueError:
				continue

	def path_yielder_eth(self):
		for path in tf.io.gfile.listdir(self.main_path):
			splitted = path.split("_")
			try:
				_, _, eth, _ = splitted

				yield self.main_path+path, int(eth)
			except ValueError:
				continue

	def image_loader(self, image):
		image = tf.io.read_file(image)
		image = tf.io.decode_jpeg(image, channels=3)
		image = tf.image.resize(image, (112, 112), method="nearest")
		image = tf.image.random_flip_left_right(image)

		return (tf.cast(image, tf.float32) - 127.5) / 128.

	def mapper(self, path, label):
		return (self.image_loader(path), label)

	def __init__(self, main_path: str, batch_size: int = 16, buffer_size: int = 10000, epochs: int = 1,
	             reshuffle_each_iteration: bool = False, test_batch=64,
	             map_to: bool = True, by: str = None):
		self.main_path = main_path.rstrip("/") + "/"

		self.yielder = self.path_yielder
		if by is not None:
			if by == "sex":
				self.yielder = self.path_yielder_sex
			elif by == "age":
				self.yielder = self.path_yielder_age
			elif by == "eth":
				self.yielder = self.path_yielder_eth
			else:
				raise Exception(f"\"by\" value must be either \"sex\", \"age\" or \"eth\", {by} is not valid!")

		self.dataset_test = None
		if test_batch > 0:
			reshuffle_each_iteration = False
			print(f"[*] reshuffle_each_iteration set to False to create a appropriate test set, this may cancelled if tf.data will fixed.")

		self.dataset = tf.data.Dataset.from_generator(self.yielder, (tf.string, tf.int32))
		if buffer_size > 0:
			self.dataset = self.dataset.shuffle(buffer_size, reshuffle_each_iteration=reshuffle_each_iteration, seed=42)

		if map_to:
			self.dataset = self.dataset.map(self.mapper, num_parallel_calls=tf.data.experimental.AUTOTUNE)
		self.dataset = self.dataset.batch(batch_size, drop_remainder=True)

		if test_batch > 0:
			self.dataset_test = self.dataset.take(int(test_batch))
			self.dataset = self.dataset.skip(int(test_batch))

		self.dataset = self.dataset.repeat(epochs)


if __name__ == '__main__':
	print("go check README.md")
